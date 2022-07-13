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

EVA_UI_BUILD_PATH="/app/eva/"
SAMPLE_UI_PATH="/app/sample"
SLEEP_TIME=5
SLEEP_TIME_EII=15
NGINX_BUILD_DIR=/usr/share/nginx/html/

mkdir -p $NGINX_BUILD_DIR

if [[ "$MODE" = "EII" ]]; then
   cd eii && python3 server.py &
   sleep ${SLEEP_TIME_EII}
   nginx
   tail -f /var/log/nginx/access.log
elif [[ "$MODE" = "EVA" ]]; then
   cp -r ./eva_ui_default/www/* $NGINX_BUILD_DIR
   sed -i 's/var default_peer_id;/var default_peer_id = 1;/g' $NGINX_BUILD_DIR/webrtc.js
   sed -i 's/wss/ws/g' $NGINX_BUILD_DIR/webrtc.js
   cp ./eva_ui_default/server.conf /etc/nginx/sites-enabled/server_eva_default.conf

   mkdir -p /usr/share/nginx/html1
   cp -r ${EVA_UI_BUILD_PATH}/build/* /usr/share/nginx/html1/
   cp ${EVA_UI_BUILD_PATH}/server.conf /etc/nginx/sites-enabled/server_eva.conf
   python3 -u ./signaling_server/simple_server.py --disable-ssl &
   sleep ${SLEEP_TIME}
   nginx
   tail -f /var/log/nginx/access.log
else
   cp -r ${SAMPLE_UI_PATH}/build/* $NGINX_BUILD_DIR
   cp ${SAMPLE_UI_PATH}/server.conf /etc/nginx/sites-enabled/server.conf
   sleep ${SLEEP_TIME}
   nginx
   tail -f /var/log/nginx/access.log
fi




