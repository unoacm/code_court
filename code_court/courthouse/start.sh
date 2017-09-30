#!/bin/bash

SCRIPT_DIR=$(dirname "$0")
cd $SCRIPT_DIR

uwsgi --ini uwsgi.ini --manage-script-name --stats 127.0.0.1:1717 #--logto /tmp/code_court.log
