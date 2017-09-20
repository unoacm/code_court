#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR

HOST_POSTGRES_PORT=43242
export CODE_COURT_DB_URI="postgresql+psycopg2://codecourt:benpass@localhost:$HOST_POSTGRES_PORT/codecourt"

./start.sh
# ./web.py
