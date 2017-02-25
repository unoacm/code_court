FROM alpine:3.5

RUN apk add --no-cache python python3 lua gcc g++ openjdk8 gfortran ruby perl nodejs bash && \
    adduser -S user

USER user

ADD ./docker_scripts /docker_scripts
