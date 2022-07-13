#!/bin/bash

# Copyright (c) 2020 Intel Corporation.

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

# to debug uncomment below line
# set -x

: "${GRAFANA_DATA_PATH:=/tmp/grafana/lib/grafana}"
: "${GRAFANA_LOGS_PATH:=/tmp/grafana/log/grafana}"
: "${GRAFANA_PLUGINS_PATH:=/tmp/grafana/lib/grafana/plugins}"

export GF_PATHS_DATA="/tmp/grafana/lib/grafana"
export GF_PATHS_LOGS="/tmp/grafana/log/grafana"
export GF_PATHS_PLUGINS="/tmp/grafana/lib/grafana/plugins"
export GF_PATHS_PROVISIONING="/tmp/grafana/conf/provisioning"
mkdir -p /tmp/grafana
cp -r $GF_PATHS_HOME/* /tmp/grafana/

python3 modify_grafana_files.py
sleep_interval=5
echo "Waiting for $sleep_interval seconds for Grafana dirs to be created"
sleep $sleep_interval

if [ $? -eq 0 ]; then
    echo "Grafana configuration files modified successfully"
    if [[ "$MODE" = "EII" ]]; then
        exec grafana-server  \
        --homepath=/tmp/grafana/                  \
        --config=/tmp/grafana/grafana.ini         \
        cfg:default.paths.data="$GRAFANA_DATA_PATH"   \
        cfg:default.paths.logs="$GRAFANA_LOGS_PATH"   \
        cfg:default.paths.plugins="$GRAFANA_PLUGINS_PATH"
    else
        exec grafana-server  \
        --homepath=$GF_PATHS_HOME /
        --config=/tmp/grafana/conf/defaults.ini         \
        cfg:default.paths.data="$GRAFANA_DATA_PATH"   \
        cfg:default.paths.logs="$GRAFANA_LOGS_PATH"   \
        cfg:default.paths.plugins="$GRAFANA_PLUGINS_PATH"
    fi
else
    echo "Failed to modify Grafana configuration files. Exiting!!!"
fi
