#!/bin/bash

docker run -it \
    --rm \
    -e POSTGRES_USER=codecourt \
    -e POSTGRES_PASSWORD=benpass \
    -e POSTGRES_DB=codecourt \
    -p 43242:5432 \
    postgres
