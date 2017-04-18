FROM alpine:edge

RUN apk update
RUN apk add --no-cache python3-dev \
                        nodejs \
                        bash \
                        musl-dev \
                        libffi-dev \
                        nodejs-npm \
                        py-virtualenv \
                        libxml2-dev \
                        libxslt-dev \
                        gcc

COPY courthouse /courthouse
COPY defendant-frontend /defendant-frontend

RUN virtualenv -p /usr/bin/python3 /env && \
        source /env/bin/activate && \
        pip install -r /courthouse/requirements.txt

RUN cd /defendant-frontend && \
        npm run build

COPY docker_scripts /docker_scripts

EXPOSE 9191

CMD ["/docker_scripts/courthouse_start.sh"]
