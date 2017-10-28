#!/usr/bin/env python

import logging
import os
import signal
import subprocess
import sys
import time

from selenium import webdriver
from docker.errors import ImageNotFound, ContainerError, APIError
from docker.api import exec_api
import docker

logging.basicConfig(level=logging.INFO)

# start postgres
POSTGRES_PORT = 45345
POSTGRES_ENVIRON = {
    "POSTGRES_USER": "codecourt",
    "POSTGRES_PASSWORD": "benpass",
    "POSTGRES_DB": "codecourt",
}

client = docker.from_env()

def main():
    postgres_container = None
    courthouse_pid = None
    try:
        logging.info("Starting postgres")
        ports = {"5432/tcp": POSTGRES_PORT}
        postgres_container = client.containers.run("postgres",
                                                   detach=True,
                                                   environment=POSTGRES_ENVIRON,
                                                   ports=ports)

        # wait for postgres to start
        iterations = 0
        while not is_postgres_up(postgres_container):
            logging.info("Waiting for postgres to come up")
            time.sleep(1)
            iterations += 1

            if iterations == 30:
                logging.fatal("Postgres failed to start")
                sys.exit(1)
        time.sleep(5)

        courthouse_pid = start_courthouse()

        run_tests()
    except ImageNotFound:
        logging.error("Postgres image not found")
        raise
    except ContainerError:
        logging.error("Failed to start postgres container")
        raise
    except APIError:
        logging.error("Failed to start postgres container")
        raise
    except Exception:
        logging.exception("Unknown exception while starting processes")
    finally:
        if postgres_container:
            postgres_container.remove(force=True)

        if courthouse_pid:
            os.kill(courthouse_pid, signal.SIGINT)


def start_courthouse():
    os.chdir("../courthouse")
    proc = subprocess.Popen(["./start_with_postgres.sh", str(POSTGRES_PORT)])

    time.sleep(1)

    with open("uwsgi-master-process.pid") as f:
        courthouse_master_pid = int(f.read())

    return courthouse_master_pid


def is_postgres_up(container):
    cmd = 'psql -U postgres -c "select 1" -d postgres'
    exec_job = client.api.exec_create(container.id, cmd)

    client.api.exec_start(exec_job['Id'])
    status = client.api.exec_inspect(exec_job['Id'])

    return status['ExitCode'] == 0


def run_tests():
    driver = webdriver.Chrome()
    driver.get("http://localhost:9191/admin")

    driver.find_element_by_css_selector

    driver.implicitly_wait(10)

if __name__ == '__main__':
    main()
