# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: MIT

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

ARG UBUNTU_IMAGE_VERSION
FROM ubuntu:${UBUNTU_IMAGE_VERSION} as builder

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends python3 \
                       python3-dev \
                       python3-pip \
                       cmake \
                       wget \
                       git

ARG EII_VERSION
RUN git clone https://github.com/open-edge-insights/eii-core.git \
    --branch ${EII_VERSION} --single-branch

ARG PKG_SRC
RUN wget ${PKG_SRC}/eii-utils-3.0.0-Linux.deb && \
    wget ${PKG_SRC}/eii-messagebus-3.0.0-Linux.deb && \
    wget ${PKG_SRC}/eii-configmanager-3.0.0-Linux.deb

# Install python dependencies
COPY ./requirements.txt /app/requirements.txt
RUN pip3 install --user -r requirements.txt;

# Build EVAM UI
COPY ./eva ./eva
RUN wget -qO- https://deb.nodesource.com/setup_14.x | bash - && \
    apt install -y nodejs

RUN cd eva && \
    npm install && \
    npm run build

RUN git clone https://github.com/dlstreamer/pipeline-server

#Build standalone app with configurable URL from grafana dasboard.
COPY ./sample ./sample
RUN cd sample && \
    npm install && \
    npm run build


RUN apt-get remove --auto-remove --purge -y python3-pip \
                       nodejs cmake wget git \
                       python3-dev \
                       python3-pip

# Build the runtime image
FROM ubuntu:$UBUNTU_IMAGE_VERSION as runtime
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app
RUN apt-get update && apt-get install -y nginx python3 libglib2.0-0  \
                       libgl1-mesa-glx  libcjson-dev \
                       libzmq3-dev python3-distutils  python3-setuptools

COPY --from=builder /app/pipeline-server/samples/webrtc/signaling  /app/signaling_server
RUN rm -f /app/signaling_server/Dockerfile
RUN rm -f /app/signaling_server/requirements.signaling.txt
RUN rm -f /app/signaling_server/build.sh

COPY . .
RUN chmod a+x run.sh
COPY --from=builder /app/eva/build  /app/eva/build
COPY --from=builder /app/sample/build  /app/sample/build
COPY --from=builder /app/eii-* /app/
COPY --from=builder /app/eii-core/common/util/*.py util/
COPY --from=builder /root/.local/lib  /app/.local/lib
COPY --from=builder /root/.local/bin  /app/.local/bin

# Installation of utils, eiimessagebus and configmgr debian packages
RUN dpkg -i /app/eii-utils-3.0.0-Linux.deb && \
    dpkg -i /app/eii-messagebus-3.0.0-Linux.deb && \
    dpkg -i /app/eii-configmanager-3.0.0-Linux.deb

ARG EII_UID
ARG EII_USER_NAME
RUN groupadd $EII_USER_NAME -g $EII_UID && \
    useradd -r -u $EII_UID -g $EII_USER_NAME $EII_USER_NAME

RUN sed -i '/modules-enabled/d' /etc/nginx/nginx.conf;
RUN chown -R ${EII_USER_NAME}:${EII_USER_NAME} /app /opt /etc/nginx/sites-enabled

ENV LD_LIBRARY_PATH ${LD_LIBRARY_PATH}:/usr/local/lib:/app
ENV PATH ${PATH}:/app/.local/bin
ENV PYTHONPATH $PYTHONPATH:/usr/local/lib/python3.8/dist-packages:/app/.local/lib/python3.8/site-packages:/app
USER $EII_USER_NAME

ENTRYPOINT ["./run.sh"]

