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

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s: %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")

SCRIPT_DIR = path.dirname(path.realpath(__file__))

EXECUTOR_IMAGE_NAME = "code-court-executor"
SHARED_DATA_DIR = path.join(SCRIPT_DIR, "share_data")
RUN_TIMEOUT = 5
writ_url = "http://localhost:9191/api/get-writ"
executioner_email = "exec@example.org"
executioner_password = "epass"
IDEAL_NUM_EXECUTORS = cpu_count()*2

def event_loop():
    # make sure that processes ignore SIGINT
    original_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
    pool = Pool(cpu_count()*2)
    signal.signal(signal.SIGINT, original_sigint_handler)

    if len(get_executor_containers()) > 0:
        logging.info("Killing orphaned executors")
        kill_all_executors()

    logging.info("Looking for writs")
    try:
        jobs = []
        while True:
            in_flight = sum(1 for x in jobs if x is not None and not x.ready())

            logging.debug("Jobs in flight: %s", in_flight)
            if logging.getLogger().isEnabledFor(logging.DEBUG):
                logging.debug("Executors running: %s", len(get_executor_containers()))

            if in_flight < IDEAL_NUM_EXECUTORS:
                for _ in range(IDEAL_NUM_EXECUTORS - in_flight):
                    jobs.append(get_and_dispatch_writ(pool))
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Exiting")
        cleanup(pool)
        sys.exit(0)
    except Exception as e:
        logging.exception("Uncaught exception, exiting")
        cleanup(pool)
        sys.exit(1)

def get_and_dispatch_writ(pool):
    try:
        writ = get_writ()
    except InvalidWritException as e:
        logging.exception("Exception while requesting writ")
        return
    except CourtHouseConnectionError:
        logging.error("Couldn't connect to courthouse")
        time.sleep(5)
        return
    except NoWritsAvailable:
        return

    logging.info("Executing writ (id: %s, lang: %s)", writ['run_id'], writ['language'])
    return pool.apply_async(execute_writ, [writ])

def cleanup(pool):
    logging.info("Waiting %s seconds for workers to finish", RUN_TIMEOUT+1)
    time.sleep(RUN_TIMEOUT+1)

    pool.terminate()
    pool.join()

    kill_all_executors()

def execute_writ(writ):
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

        timer = Timer(RUN_TIMEOUT, timout_container, [container.id, writ['run_id']])
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
    except:
        if container:
            container.remove(force=True)
            shutil.rmtree(container_shared_data_dir)
        raise
    else:
        if container:
            container.remove(force=True)
            shutil.rmtree(container_shared_data_dir)

def timeout_container(container_id, run_id):
    client = docker.from_env()

    if get_container_state(container_id)['Running']:
        logging.info("Writ timed out, id: %s", run_id)
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

def write_to_fname(fname, contents):
    with open(fname, "w+") as f:
        f.write(contents)

def make_executable(fname):
    st = os.stat(fname)
    os.chmod(fname, st.st_mode | stat.S_IEXEC)

def get_executor_containers():
    client = docker.from_env()

    # note: this is a direct api call, client.contatiners.list(all=True)
    # can fail if a container is removed while it is running
    running_containers = client.api.containers(all=True)
    exec_containers = []
    for c in running_containers:
        try:
            if c['Image'] == EXECUTOR_IMAGE_NAME:
                exec_containers.append(client.containers.get(c['Id']))
        except docker.errors.NotFound:
            pass
    return exec_containers

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

def kill_all_executors():
    client = docker.from_env()
    for c in get_executor_containers():
        logging.info("Killing %s", c.name)

        try:
            c.remove(force=True)
        except docker.errors.NotFound:
            pass

def submit_writ(writ, out):
    logging.info("Submitting writ %s", writ['run_id'])
    status = requests.post(writ['return_url'],
                           json={"output": out}, auth=HTTPBasicAuth(executioner_email, executioner_password))

class InvalidWritException(Exception):
    pass

class CourtHouseConnectionError(Exception):
    pass

class NoWritsAvailable(Exception):
    pass

if __name__ == '__main__':
    event_loop()
