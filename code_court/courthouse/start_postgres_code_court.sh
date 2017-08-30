#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR

CODE_COURT_DB_URI=postgresql+pypostgresql://codecourt:benpass@localhost:43242/codecourt ./web.py
