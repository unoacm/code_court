#!/bin/bash

until curl postgres:5432 2>&1  | grep -q '52'; do
    echo "Waiting for postgres to start..."
    sleep 2
done

source /env/bin/activate

cd /courthouse
./start.sh
