#!/usr/bin/env python

import json
import logging
import os
import stat
import subprocess
import sys
import tempfile
import time
import traceback
import uuid

import requests

from requests.auth import HTTPBasicAuth

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

writ_url = "http://localhost:9191/api/get-writ"
executioner_email = "exec@example.org"
executioner_password = "epass"


def _main():
    try:
        event_loop()
    except KeyboardInterrupt:
        logging.info("Exiting")
        sys.exit(0)


def event_loop():
    logging.info("Looking for writs")
    while True:
        overall_stime = time.time()
        try:
            writ = get_writ()
        except InvalidWritException as e:
            print(traceback.format_exc())
            time.sleep(1)
            continue

        if writ is None:
            time.sleep(1)
            continue

        logging.info("Executing writ (id: %s, lang: %s)", writ['run_id'], writ['language'])
        stime = time.time()
        out = run_writ(writ)

        stime = time.time()
        submit_writ(writ['return_url'], out)


def get_writ():
    try:
        r = requests.get(writ_url, auth=HTTPBasicAuth(executioner_email, executioner_password))
    except Exception as e:
        raise InvalidWritException("Writ request returned exception: %s" % traceback.format_exc())

    if r.status_code != 200:
        raise InvalidWritException("Received non-200 status code: %s" % r.status_code)

    writ = r.json()

    if writ['status'] != 'found':
        return None

    if 'source_code' not in writ:
        raise InvalidWritException("Received invalid writ, missing source_code")

    if 'run_script' not in writ:
        raise InvalidWritException("Received invalid writ, missing run_script")

    if 'input' not in writ:
        raise InvalidWritException("Received invalid writ, missing input")

    if 'return_url' not in writ:
        raise InvalidWritException("Received invalid writ, missing return_url")

    return writ


def run_writ(writ):
    # write run script
    run_script_path = "/tmp/{}".format(uuid.uuid4().hex)
    with open(run_script_path, "w+") as f:
        f.write(writ['run_script'])
        f.flush()

    # make run script executable
    st = os.stat(run_script_path)
    os.chmod(run_script_path, st.st_mode | stat.S_IEXEC)

    # write source code
    with tempfile.NamedTemporaryFile(mode="w+") as source_code:
        source_code.write(writ['source_code'])
        source_code.flush()

        # write input file
        with tempfile.NamedTemporaryFile(mode="w+") as input_file:
            input_file.write(writ['input'])
            input_file.flush()

            # run submssion
            p = subprocess.Popen([run_script_path, input_file.name, source_code.name], stdout=subprocess.PIPE)
            out = p.communicate()[0]
            return out

    os.remove(run_script_path)


def submit_writ(return_url, out):
    r = requests.get(writ_url, )
    status = requests.post(return_url,
                           json={"output": out.decode("utf-8")}, auth=HTTPBasicAuth(executioner_email, executioner_password))


class InvalidWritException(Exception):
    pass

if __name__ == '__main__':
    _main()
