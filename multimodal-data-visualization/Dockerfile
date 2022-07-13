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

ARG GRAFANA_VERSION
ARG ALPINE_VERSION
FROM alpine:$ALPINE_VERSION as builder
WORKDIR /app
RUN apk update && \
    apk add wget \
    cmake \
    git \
    cjson-dev \
    zeromq-dev  \
    gcc \
    libc-dev \
    py3-pip \
    python3-dev

RUN pip3 install cython
ARG PKG_SRC
RUN wget ${PKG_SRC}/eii-utils-3.0.0-r0.apk && \
    wget ${PKG_SRC}/eii-messagebus-3.0.0-r0.apk && \
    wget ${PKG_SRC}/eii-configmanager-3.0.0-r0.apk

# Installation of utils, eiimessagebus and configmgr debian packages
RUN apk add --allow-untrusted /app/eii-utils-3.0.0-r0.apk && \
    apk add --allow-untrusted /app/eii-messagebus-3.0.0-r0.apk && \
    apk add --allow-untrusted /app/eii-configmanager-3.0.0-r0.apk

ARG EII_VERSION

# Install Python Bindings for EII packages
RUN git clone https://github.com/open-edge-insights/eii-configmgr --branch ${EII_VERSION} --single-branch
RUN cd  eii-configmgr/python && python3 setup.py.in install --user && cd /app

RUN git clone https://github.com/open-edge-insights/eii-messagebus --branch ${EII_VERSION} --single-branch
RUN cd eii-messagebus/python && python3 setup.py install --user && cd /app

RUN git clone https://github.com/open-edge-insights/eii-core.git --branch ${EII_VERSION} --single-branch

RUN apk del wget \
    cmake \
    wget \
    git \
    cjson-dev \
    zeromq-dev  \
    gcc \
    libc-dev \
    py3-pip \
    python3-dev

FROM grafana/grafana:$GRAFANA_VERSION as runtime

USER root
WORKDIR /app

RUN apk update && apk add python3

COPY . /app/
RUN chmod +x run.sh

ARG EII_UID
ARG EII_USER_NAME

RUN addgroup -S $EII_USER_NAME && adduser -S $EII_UID -G $EII_USER_NAME

# Install Grafana Plugins
RUN grafana-cli --pluginsDir "$GF_PATHS_HOME/lib/grafana/plugins" plugins install ryantxu-ajax-panel
RUN grafana-cli --pluginsDir "$GF_PATHS_HOME/lib/grafana/plugins" plugins install yesoreyeram-infinity-datasource


COPY --from=builder /usr/lib/lib* /usr/lib/
COPY --from=builder /app/eii-core/common/util/*.py util/
COPY --from=builder /root/.local/lib  /app/.local/lib

RUN chown -R ${EII_UID}:${EII_UID} /app

ENV PYTHONPATH $PYTHONPATH:/app/.local/lib/python3.9/site-packages:/app
ENV LD_LIBRARY_PATH ${LD_LIBRARY_PATH}:/usr/local/lib:/app

USER $EII_UID:$EII_USER_NAME
ENTRYPOINT ["./run.sh"]
