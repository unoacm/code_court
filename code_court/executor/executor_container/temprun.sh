#!/bin/bash

if [[ ! -d /tmp/share ]]; then
    mkdir /tmp/share
fi

docker run -it -v /tmp/share:/share:rw --rm --user user code-court-executor bash
