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
                        libpq \
                        gcc \
                        postgresql-dev


COPY courthouse/requirements.txt /tmp/courthouse_requirements.txt
RUN virtualenv -p /usr/bin/python3 /env && \
        source /env/bin/activate && \
        pip install -r /tmp/courthouse_requirements.txt

COPY defendant-frontend /defendant-frontend
RUN cd /defendant-frontend && \
        npm run build

COPY courthouse /courthouse

COPY docker_scripts /docker_scripts

# ENV CODE_COURT_PRODUCTION true

EXPOSE 9191

CMD ["/docker_scripts/courthouse_start.sh"]
