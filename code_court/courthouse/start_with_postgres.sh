#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR

POSTGRES_PORT=43242
if [[ $# -eq 1 ]]; then
    POSTGRES_PORT=$1
fi

export CODE_COURT_DB_URI="postgresql+psycopg2://codecourt:benpass@localhost:$POSTGRES_PORT/codecourt"
echo "Starting courthouse with DB_URI of: $CODE_COURT_DB_URI"

./start.sh
# ./web.py
