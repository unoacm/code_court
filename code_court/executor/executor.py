#!/usr/bin/env python

import logging
import os
import random
import sched
import shutil
import stat
import signal
import string
import sys
import time
import traceback
import uuid

from os import path
from threading import Timer
from multiprocessing import Pool, cpu_count

from requests.auth import HTTPBasicAuth

import docker
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

SCRIPT_DIR = path.dirname(path.realpath(__file__))

EXECUTOR_IMAGE_NAME = "code-court-executor"
SHARED_DATA_DIR = path.join(SCRIPT_DIR, "share_data")
RUN_TIMEOUT = 5
writ_url = "http://localhost:9191/api/get-writ"
executioner_email = "exec@example.org"
executioner_password = "epass"

def event_loop():
    original_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
    pool = Pool(cpu_count())
    signal.signal(signal.SIGINT, original_sigint_handler)

    logging.info("Looking for writs")
    try:
        while True:
            num_executors = len(get_executor_containers())
            ideal_num_executors = cpu_count()

            if num_executors < ideal_num_executors:
                for _ in range(ideal_num_executors - num_executors):
                    pool.apply_async(process_writ)
            time.sleep(2)
    except KeyboardInterrupt:
        logging.info("Terminating workers")

        pool.terminate()
        pool.join()

        time.sleep(1)

        # kill all executor containers
        client = docker.from_env()
        for c in get_executor_containers():
            logging.info("Killing %s", c.name)

            try:
                c.remove(force=True)
            except docker.errors.NotFound:
                pass

        sys.exit(0)

def process_writ():
    try:
        writ = get_writ()
    except InvalidWritException as e:
        logging.exception("Exception while requesting writ")
        return

    if writ is None:
        return

    logging.info("Executing writ (id: %s, lang: %s)", writ['run_id'], writ['language'])

    client = docker.from_env()
    runner_str = writ['run_script']
    runner_str = runner_str.replace("$1", "/share/input")
    runner_str = runner_str.replace("$2", "/share/program")

    input_str = writ['input']
    program_str = writ['source_code']

    container_ident = "{}-{}-{}".format(writ['run_id'], writ['language'], str(uuid.uuid4()))

    container_shared_data_dir = path.join(SHARED_DATA_DIR, container_ident)
    os.makedirs(container_shared_data_dir)

    shared_volumes = {
        container_shared_data_dir: {
            "bind": "/share",
            "mode": "rw"
        }
    }

    container_name = "executor-{}".format(container_ident)

    create_share_files(container_shared_data_dir, runner_str, input_str, program_str)

    container = None
    try:
        container = client.containers.run(EXECUTOR_IMAGE_NAME,
                                                 "tail -f /dev/null",
                                                 detach=True,
                                                 volumes=shared_volumes,
                                                 name=container_name)

        # TODO: check what happens if tons of output is sent
        stream = container.exec_run("/share/runner", stream=True)

        timer = Timer(RUN_TIMEOUT, kill_container, [container.id])
        try:
            timer.start()
            out = []
            for line in stream:
                out.append(line.decode("utf-8"))

            if is_container_running(container.id):
                container.kill()

            submit_writ(writ, "".join(out))
        finally:
            timer.cancel()
    finally:
        if container:
            if is_container_running(container.id):
                container.kill()
            time.sleep(.5)
            container.remove()

            shutil.rmtree(container_shared_data_dir)

def kill_container(container_id):
    client = docker.from_env()

    if get_container_state(container_id)['Running']:
        logging.info("Writ timed out")
        try:
            client.containers.get(container_id).kill()
        except docker.errors.APIError:
            pass

def is_container_running(container_id):
    return get_container_state(container_id)['Running']

def get_container_state(container_id):
    client = docker.from_env()
    return client.containers.get(container_id).attrs['State']

def create_share_files(share_folder, runner_str, input_str, program_str):
    runner_file = path.join(share_folder, "runner")
    write_to_fname(runner_file, runner_str)
    make_executable(runner_file)

    input_file = path.join(share_folder, "input")
    write_to_fname(input_file, input_str)
    make_executable(input_file)

    program_file = path.join(share_folder, "program")
    write_to_fname(program_file, program_str)
    make_executable(program_file)

def get_random_letters(length):
    ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(length))

def write_to_fname(fname, contents):
    with open(fname, "w+") as f:
        f.write(contents)

def make_executable(fname):
    st = os.stat(fname)
    os.chmod(fname, st.st_mode | stat.S_IEXEC)

def get_executor_containers():
    client = docker.from_env()

    containers = []
    for c in client.containers.list(all=True):
        try:
            if c.attrs.get("Config", {}).get("Image") == EXECUTOR_IMAGE_NAME:
                containers.append(c)
        except docker.errors.NotFound:
            pass
    return containers

def get_writ():
    try:
        r = requests.get(writ_url, auth=HTTPBasicAuth(executioner_email, executioner_password))
    except Exception as e:
        raise InvalidWritException("Writ request returned exception: %s" % traceback.format_exc())

    if r.status_code == 404:
        return None

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

def submit_writ(writ, out):
    logging.info("Submitting writ %s", writ['run_id'])
    status = requests.post(writ['return_url'],
                           json={"output": out}, auth=HTTPBasicAuth(executioner_email, executioner_password))

class InvalidWritException(Exception):
    pass

if __name__ == '__main__':
    event_loop()
