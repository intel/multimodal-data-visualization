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
import threading
import queue
import secrets
import shlex
from flask import Flask, render_template, Response, request, session
import cv2
import numpy as np
import math
import subprocess
import cfgmgr.config_manager as cfg
from util.log import configure_logging
from util.common import Visualizer

TEXT = 'Disconnected'
TEXTPOSITION = (10, 110)
TEXTFONT = cv2.FONT_HERSHEY_PLAIN
TEXTCOLOR = (255, 255, 255)

# Config manager initialization
ctx = cfg.ConfigMgr()
app_cfg = ctx.get_app_config()
dev_mode = ctx.is_dev_mode()
topics_list = []
topic_config_list = []
queue_dict = {}

# Initializing logger
log = configure_logging(os.getenv('PY_LOG_LEVEL', 'DEBUG').upper(), __name__,
                        dev_mode)

# Visualization related variables
FRAME_QUEUE_SIZE = 10

# Initializing flask related variables
NONCE = secrets.token_urlsafe(8)
APP = Flask(__name__)

# For Secure Session Cookie
APP.config.update(SESSION_COOKIE_SECURE=True,
                  SESSION_COOKIE_SAMESITE='Lax')
APP.secret_key = os.urandom(24)
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
            topic_config = (topic, msgbus_config)
            topic_config_list.append(topic_config)
            topics_list.append(topic)
            queue_dict[topic] = queue.Queue(maxsize=FRAME_QUEUE_SIZE)
except Exception as e:
    log.warning(f"No subscriber instances found {e}")


def msg_bus_subscriber(topic_name, logger, json_config):
    """msg_bus_subscriber is the ZeroMQ callback to
    subscribe to classified results
    """
    visualizer = Visualizer(queue_dict, logger,
                            labels=json_config["labels"],
                            draw_results=json_config["draw_results"])

    for topic_config in topic_config_list:

        topic, msgbus_cfg = topic_config

        if topic_name == topic:
            callback_thread = threading.Thread(target=visualizer.callback,
                                               args=(msgbus_cfg, topic,))
            callback_thread.start()
            break


def get_blank_image(text):
    """Get Blank Images
    """
    blank_image_shape = (130, 200, 3)
    blank_image = np.zeros(blank_image_shape, dtype=np.uint8)
    cv2.putText(blank_image, text, TEXTPOSITION,
                TEXTFONT, 1.5, TEXTCOLOR, 2, cv2.LINE_AA)
    _, jpeg = cv2.imencode('.jpg', blank_image)
    final_image = jpeg.tobytes()
    return final_image


def get_image_data(topic_name):
    """Get the Images from Zmq
    """
    logger = configure_logging(os.environ['PY_LOG_LEVEL'].upper(),
                               __name__, dev_mode)
    try:
        final_image = get_blank_image(TEXT)
        msg_bus_subscriber(topic_name, logger, app_cfg)
        while True:
            if topic_name in queue_dict.keys():
                if not queue_dict[topic_name].empty():
                    frame = queue_dict[topic_name].get()
                    ret, jpeg = cv2.imencode('.jpg', frame)
                    del frame
                    final_image = jpeg.tobytes()
                    del jpeg
            else:
                raise Exception(f"Topic: {topic_name} doesn't exist")

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + final_image +
                   b'\r\n\r\n')
    except KeyboardInterrupt:
        log.exception('Quitting due to keyboard interrupt...')
    except Exception as err:
        log.exception(f'Error during execution: {err}')


def set_header_tags(response):
    """Local function to set secure response tags"""
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=1024000;\
                                                    includeSubDomains'
    return response


@APP.route('/')
def index():
    """Video streaming home page."""

    response = APP.make_response(render_template('index.html',
                                                 nonce=NONCE))
    return set_header_tags(response)


@APP.route('/topics', methods=['GET'])
def return_topics():
    """Returns topics list over http
    """
    return Response(str(topics_list))


@APP.route('/<topic_name>', methods=['GET'])
def render_image(topic_name):
    """Renders images over http
    """
    if topic_name in topics_list:
        return Response(get_image_data(topic_name),
                        mimetype='multipart/x-mixed-replace;\
                                  boundary=frame')

    return Response("Invalid Request")


def main():
    # Multi instance variables
    nginx_conf_path = "/etc/nginx/sites-enabled/"
    server_cert_name = "/opt/server.crt"
    server_key_name = "/opt/server.key"
    server_content = ""
    if not dev_mode:
        nginx_server_prod_conf = "/app/eii/server_prod.conf.template"
        server_cert = app_cfg["server_cert"]
        server_key = app_cfg["server_key"]

        # Since Python SSL Load Cert Chain Method is not having option to load
        # Cert from Variable. So for now we are going below method

        server_cert_temp = open(server_cert_name, "w")
        server_key_temp = open(server_key_name, "w")

        server_cert_temp.write(server_cert)
        server_cert_temp.seek(0)

        server_key_temp.write(server_key)
        server_key_temp.seek(0)

        server_cert_temp.close()
        server_key_temp.close()
        with open(nginx_server_prod_conf, "r") as _file:
            server_content = _file.read()
            server_content = server_content.replace("$CERT_FILE", server_cert_name)
            server_content = server_content.replace("$CERT_KEY", server_key_name)

    else:
        with open("/app/eii/server.conf") as _file:
            server_content = _file.read()

    # All browser security limitations retrict flask from serving
    # more than 6 requests
    # Hence, running a Gunicorn server instance for every 6 streams

    internal_port = 3000
    if dev_mode:
        port = app_cfg['dev_port']
    else:
        port = app_cfg['port']

    processes = []
    for i in range(0, (math.ceil(num_of_subs / 6))):
        if not dev_mode:
            command = f"gunicorn -w6 --timeout 0 -b 0.0.0.0:{internal_port} --certfile={server_cert_name} " \
                      f"--keyfile={server_key_name} server:APP"
        else:
            command = f"gunicorn -w6 --timeout 0 -b 0.0.0.0:{internal_port} server:APP"
        command = shlex.split(command)
        content = server_content.replace("$PORT", str(port))
        content = content.replace("$INTERNAL_PORT", str(internal_port))
        with open(os.path.join(nginx_conf_path, f"server_{port}.conf"), "w") as _file:
            _file.write(content)
        internal_port = internal_port + 1
        port = port + 1
        process = subprocess.Popen(command)
        processes.append(process)

    for process in processes:
        process.wait()


if __name__ == "__main__":
    main()



