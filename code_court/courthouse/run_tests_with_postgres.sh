#!/bin/bash

HOST_POSTGRES_PORT=21381
export CODE_COURT_DB_URI="postgresql+psycopg2://codecourt:benpass@localhost:$HOST_POSTGRES_PORT/codecourt"

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR

docker run -it \
    -d \
    -e POSTGRES_USER=codecourt \
    -e POSTGRES_PASSWORD=benpass \
    -e POSTGRES_DB=codecourt \
    -p $HOST_POSTGRES_PORT:5432 \
    postgres > /dev/null
CONTAINER_ID=$(docker ps -l -a | grep -v "CONTAINER ID" | awk '{print $1}')

until curl localhost:$HOST_POSTGRES_PORT 2>&1  | grep -q '52'; do
    echo "Waiting for postgres to start..."
    sleep 2
done

echo "Started postgres, docker id: $CONTAINER_ID"

nosetests

STATUS=$?


echo "Stopping postgres $CONTAINER_ID"
docker rm -f $CONTAINER_ID > /dev/null

exit $STATUS
