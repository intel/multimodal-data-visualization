# Copyright (c) 2019 Intel Corporation.

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Grafana Service
"""

import os
import shutil
import json
import tempfile
import copy
import queue
import math
import cfgmgr.config_manager as cfg
from util.log import configure_logging

# Initializing Grafana related variables
TMP_DIR = tempfile.gettempdir()
GRAFANA_DIR = os.path.join(TMP_DIR, "grafana")
CERT_FILE = "{}/server_cert.pem".format(GRAFANA_DIR)
KEY_FILE = "{}/server_key.pem".format(GRAFANA_DIR)
CA_FILE = "{}/ca_cert.pem".format(GRAFANA_DIR)
CONF_FILE = "{}/grafana.ini".format(GRAFANA_DIR)
TEMP_DS = "{}/conf/provisioning/datasources/datasource.yml".format(GRAFANA_DIR)
DASHBOARD_DEST = "{}/conf/provisioning/dashboards/dashboard.json".format(GRAFANA_DIR)
DASHBOARD_YML = "{}/conf/provisioning/dashboards/dashboard.yml".format(GRAFANA_DIR)

try:
    # Config manager initialization
    ctx = cfg.ConfigMgr()
    app_cfg = ctx.get_app_config()
    dev_mode = ctx.is_dev_mode()
    # Initializing logger
    log = configure_logging(os.getenv('PY_LOG_LEVEL', 'DEBUG').upper(), __name__,
                            dev_mode)

except Exception as error:
    print("Not running in EII mode, cannot connect to config manager")
topics_list = []
topic_config_list = []
queue_dict = {}


# Visualization related variables
FRAME_QUEUE_SIZE = 10


def modify_cert(conf):
    """This function modifies each of the certs
       (ca cert, client cert and client key)
       as a single line string to make it compatible with Grafana.
    """
    fpd = open(conf["trustFile"], 'r')
    lines = fpd.readlines()
    tls_ca_cert = "\\n".join([line.strip() for line in lines])
    fpd = open(conf["certFile"], 'r')
    lines = fpd.readlines()
    tls_client_cert = "\\n".join([line.strip() for line in lines])
    fpd = open(conf["keyFile"], 'r')
    lines = fpd.readlines()
    tls_client_key = "\\n".join([line.strip() for line in lines])

    cert = {'tls_ca_cert': tls_ca_cert, 'tls_client_cert': tls_client_cert, 'tls_client_key': tls_client_key}

    return cert


def generate_prod_datasource_file(db_config, conf):
    """This function generates the grafana datasource config for PROD mode
    """

    cert_dict = modify_cert(conf)
    db_tags = ["user", "password", "database"]
    tls_config = {"tlsAuth": "true",
                  "tlsAuthWithCACert": "true",
                  "tlsCACert": cert_dict['tls_ca_cert'],
                  "tlsClientCert": cert_dict['tls_client_cert'],
                  "tlsClientKey": cert_dict['tls_client_key']}

    with open('./eii/datasources.yml', 'r') as fin:
        with open(TEMP_DS, "w+") as fout:
            for line in fin.readlines():
                not_done = True
                for tag in db_tags:
                    if tag + ':' in line:
                        line = line.replace('""', db_config[tag])
                        fout.write(line)
                        not_done = False

                for key, value in tls_config.items():
                    if key + ':' in line:
                        if key in ("tlsAuth", "tlsAuthWithCACert"):
                            line = line.replace('false', value)
                        else:
                            line = line.replace('"..."', '"' + value + '"')
                        fout.write(line)
                        not_done = False

                if "url:" in line:
                    line = line.replace('http://$INFLUX_SERVER:8086',
                                        'https://$INFLUX_SERVER:8086')
                    fout.write(line)
                    not_done = False

                if not_done:
                    fout.write(line)


def generate_prod_ini_file():
    """This function generates the grafana.ini config for PROD mode
    """
    connection_config = {"protocol": "https",
                         "cert_file": CERT_FILE,
                         "cert_key": KEY_FILE,
                         "http_addr": os.environ['GRAFANA_SERVER']}

    with open('./eii/grafana.ini', 'r') as fin:
        with open(CONF_FILE, "w") as fout:
            for line in fin.readlines():
                not_done = True
                for key, value in connection_config.items():
                    if ";" + key + " =" in line:
                        if key == "protocol":
                            line = line.replace(';' + key + ' = http',
                                                key + ' = ' + value)
                            fout.write(line)
                            not_done = False
                        elif key == "http_addr":
                            if os.environ['GRAFANA_SERVER']:
                                value = os.environ['GRAFANA_SERVER']
                            line = line.replace(';' + key + ' =',
                                                key + ' = ' + value)
                            fout.write(line)
                            not_done = False
                        else:
                            line = line.replace(';' + key + ' =',
                                                key + ' = ' + value)
                            fout.write(line)
                            not_done = False

                if not_done:
                    fout.write(line)


def generate_dev_datasource_file(db_config):
    """This function generates the grafana datasource config for DEV mode
    """
    with open('./eii/datasources.yml', 'r') as fin:
        with open(TEMP_DS, "w+") as fout:
            for line in fin.readlines():
                if "user:" in line:
                    line = line.replace('""', db_config['user'])
                    fout.write(line)
                elif "password:" in line:
                    line = line.replace('""', db_config['password'])
                    fout.write(line)
                elif "database:" in line:
                    line = line.replace('""', db_config['database'])
                    fout.write(line)
                else:
                    fout.write(line)


def generate_dev_ini_file():
    """This function generates the grafana.ini config for DEV mode
    """
    with open('./eii/grafana.ini', 'r') as fin:
        with open(CONF_FILE, "w") as fout:
            for line in fin.readlines():
                if ";http_addr =" in line:
                    host = os.environ['GRAFANA_SERVER']
                    line = line.replace(';http_addr =', 'http_addr = ' + host)
                    fout.write(line)
                else:
                    fout.write(line)


def read_config(app_cfg):
    """This function reads the InfluxDBConnector config
       from etcd to fetch the InfluxDB credentials
    """
    influx_uname = os.environ["INFLUXDB_USERNAME"]
    influx_pwd = os.environ["INFLUXDB_PASSWORD"]
    dbname = app_cfg["influxdb"]["dbname"]

    db_conf = {'user': influx_uname, 'password': influx_pwd, 'database': dbname}

    return db_conf


def copy_eii_config_files():
    """This function copies the modified grafana config files
    """
    shutil.copy('./eii/dashboards.yml', DASHBOARD_YML)


def get_grafana_config(app_cfg):
    """This function reads the certificates from etcd
       and writes it to respective files.
    """
    # Set path to certs here
    ca_cert = app_cfg["ca_cert"]
    server_cert = app_cfg["server_cert"]
    server_key = app_cfg["server_key"]

    with open(CA_FILE, 'w') as fpd:
        fpd.write(ca_cert)
    os.chmod(CA_FILE, 0o400)

    with open(CERT_FILE, 'w') as fpd:
        fpd.write(server_cert)
    os.chmod(CERT_FILE, 0o400)

    with open(KEY_FILE, 'w') as fpd:
        fpd.write(server_key)
    os.chmod(KEY_FILE, 0o400)

    eii_cert_path = {'trustFile': CA_FILE, 'certFile': CERT_FILE, 'keyFile': KEY_FILE}

    return eii_cert_path


def modify_multi_instance_dashboard():
    """To modify dashboard in case of multiple
       video streams
    """
    js = None
    with open('./eii/dashboard.json', "rb") as f:
        js = json.loads(f.read())
        default_panel = js['panels'][1]
        default_url = js['panels'][1]['url']
        default_title = js['panels'][1]['title']
        del js['panels'][1]
        for i in range(0, len(topics_list)):
            multi_instance_panel = copy.deepcopy(default_panel)
            multi_instance_panel['url'] = \
                default_url.replace(topics_list[0], topics_list[i])
            multi_instance_panel['url'] = \
                multi_instance_panel['url'].replace('127.0.0.1',
                                                    os.environ['HOST_IP'])
            if not dev_mode:
                multi_instance_panel['url'] = \
                    multi_instance_panel['url'].replace('http', 'https')
            if dev_mode:
                multi_instance_panel['url'] = \
                    multi_instance_panel['url'].replace(str(app_cfg['port']),
                                                        str(app_cfg['dev_port']))
            multi_instance_panel['title'] = \
                default_title.replace(topics_list[0], topics_list[i])
            multi_instance_panel['id'] = \
                multi_instance_panel['id'] + i
            multi_instance_panel['gridPos']['y'] = \
                int(multi_instance_panel['gridPos']['y'])*(i+1)
            js['panels'].append(multi_instance_panel)

        for i in range(1, len(topics_list)+1):
            port = js['panels'][i]['url'].split(":")[-1].split("/")[0]
            new_port = int(port) + (math.ceil(i/6) - 1)
            print("port : ", new_port)
            js['panels'][i]['url'] = js['panels'][i]['url'].replace(port,
                                                                    str(new_port))
    with open(DASHBOARD_DEST, "w") as f:
        json.dump(js, f, ensure_ascii=False, indent=4)


def update_dashboard(mode):
    dashboard = f'./{mode}/dashboard.json'
    with open(dashboard, "rb") as f:
        data = f.read().decode()
        if os.environ['HOST_IP'] != "":
            data = data.replace('127.0.0.1', os.environ['HOST_IP'])
    with open(DASHBOARD_DEST, "w") as f:
        f.write(data)


def copy_eva_config_files():
    shutil.copy('./eva/dashboards.yml', DASHBOARD_YML)
    shutil.copy('./eva/datasources.yml', TEMP_DS)


def copy_sample_dashboard_config():
    shutil.copy('./sample/dashboards.yml', DASHBOARD_YML)


def main():
    """Main method for grafana
    """
    mode = os.environ.get("MODE", "")
    if mode == "EII":
        db_config = read_config(app_cfg)
        if not dev_mode:
            eii_cert_path = get_grafana_config(app_cfg)
            log.info("generating prod mode config files for grafana")
            generate_prod_datasource_file(db_config, eii_cert_path)
            generate_prod_ini_file()
        else:
            log.info("generating dev mode config files for grafana")
            generate_dev_datasource_file(db_config)
            generate_dev_ini_file()

        try:
            # Initializing subscriber for multiple streams
            num_of_subs = ctx.get_num_subscribers()
            if num_of_subs > 0:
                for index in range(0, num_of_subs):
                    sub_ctx = ctx.get_subscriber_by_index(index)
                    msgbus_config = sub_ctx.get_msgbus_config()
                    topic = sub_ctx.get_topics()[0]
                    # Adding topic & msgbus_config to
                    # topic_config tuple
                    if not "point" in topic:
                        topic_config = (topic, msgbus_config)
                        topic_config_list.append(topic_config)
                        topics_list.append(topic)
                        queue_dict[topic] = queue.Queue(maxsize=FRAME_QUEUE_SIZE)
                modify_multi_instance_dashboard()
        except Exception as e:
            log.warn(f"No subscriber instances found {e}")
        copy_eii_config_files()
    elif mode == "EVA":
        update_dashboard("eva")
        copy_eva_config_files()
    else:
        update_dashboard("sample")
        copy_sample_dashboard_config()


if __name__ == "__main__":
    main()
