#!/bin/bash

SCRIPT_DIR=$(dirname "$0")

cd $SCRIPT_DIR

# gunicorn web:app -c gunicorn_config.py

uwsgi --ini uwsgi.ini --manage-script-name --mount /=web:app --logto /tmp/code_court.log
