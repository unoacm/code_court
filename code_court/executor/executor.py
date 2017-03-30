#!/usr/bin/env python

import logging
import os
import stat
import signal
import sys
import time
import traceback
import uuid

from os import path

from requests.auth import HTTPBasicAuth

import docker
import requests

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s: %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")

SCRIPT_DIR = path.dirname(path.realpath(__file__))

EXECUTOR_IMAGE_NAME = "code-court-executor"
SHARED_DATA_DIR = path.join(SCRIPT_DIR, "share_data")

writ_url = "http://localhost:9191/api/get-writ"
RETURN_URL = "http://localhost:9191/api/return-without-run"
executioner_email = "exec@example.org"
executioner_password = "epass"

RUN_TIMEOUT = 5
CPU_PERIOD = 500000
MEM_LIMIT = "128m"
PID_LIMIT = 50
MEM_SWAPPINESS = 0 # disable container swapping
CONTAINER_USER = "user"
OUTPUT_LIMIT = 100000 # chars

client = docker.from_env()

def main():
    while True:
        try:
            writ = get_writ()
        except InvalidWritException as e:
            logging.exception("Exception while requesting writ")
            continue
        except CourtHouseConnectionError:
            logging.error("Couldn't connect to courthouse")
            time.sleep(5)
            continue
        except NoWritsAvailable:
            continue

        logging.info("Executing writ (id: %s, lang: %s)", writ['run_id'], writ['language'])

        input_str = writ['input']
        program_str = writ['source_code']
        runner_str = writ['run_script']
        runner_str = runner_str.replace("$1", "/share/input")
        runner_str = runner_str.replace("$2", "/share/program")

        container_ident = "{}-{}-{}".format(writ['run_id'], writ['language'], str(uuid.uuid4()))

        container_shared_data_dir = path.join(SHARED_DATA_DIR, container_ident)
        os.makedirs(container_shared_data_dir)

        create_share_files(container_shared_data_dir, runner_str, input_str, program_str)

        shared_volumes = {
            container_shared_data_dir: {
                "bind": "/share",
                "mode": "ro"
            }
        }

        signal.signal(signal.SIGALRM, raise_timeout)
        signal.alarm(RUN_TIMEOUT)

        container = None
        try:
            container = client.containers.run(EXECUTOR_IMAGE_NAME,
                                                     "/share/runner",
                                                     detach=True,
                                                     working_dir="/share",
                                                     volumes=shared_volumes,
                                                     user=CONTAINER_USER,
                                                     network_disabled=True,
                                                     read_only=False,
                                                     mem_swappiness=MEM_SWAPPINESS,
                                                     pids_limit=PID_LIMIT,
                                                     cpu_period=CPU_PERIOD,
                                                     mem_limit=MEM_LIMIT)

            out = []
            rolling_size = 0
            for line in container.logs(stream=True):
                chunk = line.decode("utf-8")
                rolling_size += len(chunk)

                if rolling_size > OUTPUT_LIMIT:
                    raise OutputLimitExceeded()

                out.append(chunk)
            signal.alarm(0)
        except TimedOutException as e:
            logging.info("Timed out writ %s", writ.get('run_id'))
            submit_writ(writ, "Error: Timed out")
            continue
        except OutputLimitExceeded as e:
            logging.info("Output limit exceeded on writ %s", writ.get('run_id'))
            submit_writ(writ, "Error: Output limit exceeded")
            continue
        finally:
            signal.alarm(0)
            if container:
                container.remove(force=True)

        submit_writ(writ, "".join(out))


def create_share_files(share_folder, runner_str, input_str, program_str):
    files = {
        "runner": runner_str,
        "input": input_str,
        "program": program_str
    }

    for fname, contents in files.items():
        loc = path.join(share_folder, fname)
        with open(loc, "w+") as f:
            f.write(contents.replace("\r\n", "\n"))

        st = os.stat(loc)
        os.chmod(loc, st.st_mode | stat.S_IEXEC)


def get_writ():
    try:
        r = requests.get(writ_url, auth=HTTPBasicAuth(executioner_email, executioner_password))
    except Exception as e:
        raise CourtHouseConnectionError("Couldn't fetch writ from courthouse: %s" % traceback.format_exc())

    if r.status_code == 404:
        raise NoWritsAvailable()

    if r.status_code != 200:
        raise InvalidWritException("Received non-200 status code: %s" % r.status_code)

    writ = r.json()

    if writ['status'] != 'found':
        raise NoWritsAvailable()

    if 'source_code' not in writ:
        raise InvalidWritException("Received invalid writ, missing source_code")

    if 'run_script' not in writ:
        raise InvalidWritException("Received invalid writ, missing run_script")

    if 'input' not in writ:
        raise InvalidWritException("Received invalid writ, missing input")

    if 'return_url' not in writ:
        raise InvalidWritException("Received invalid writ, missing return_url")

    return writ

def submit_writ(writ, out):
    logging.info("Submitting writ %s", writ['run_id'])
    status = requests.post(writ['return_url'],
                           json={"output": out}, auth=HTTPBasicAuth(executioner_email, executioner_password))

def raise_timeout(signum, frame):
    raise TimedOutException()

class OutputLimitExceeded(Exception):
    pass

class TimedOutException(Exception):
    pass

class InvalidWritException(Exception):
    pass

class CourtHouseConnectionError(Exception):
    pass

class NoWritsAvailable(Exception):
    pass

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Exiting")
        sys.exit(0)
    except Exception as e:
        logging.exception("Uncaught exception, exiting")
        sys.exit(1)
