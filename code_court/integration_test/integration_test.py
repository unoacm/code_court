#!/usr/bin/env python

import logging
import os
import signal
import subprocess
import time

from selenium import webdriver
from docker.errors import ImageNotFound, ContainerError, APIError
import docker

logging.basicConfig(level=logging.INFO)

# start postgres
POSTGRES_PORT = 45345
POSTGRES_ENVIRON = {
    "POSTGRES_USER": "codecourt",
    "POSTGRES_PASSWORD": "benpass",
    "POSTGRES_DB": "codecourt",
}

def main():
    postgres_container = None
    courthouse_pid = None
    try:
        logging.info("Starting postgres")
        client = docker.from_env()
        ports = {"5432/tcp": POSTGRES_PORT}
        postgres_container = client.containers.run("postgres",
                                                   detach=True,
                                                   environment=POSTGRES_ENVIRON,
                                                   ports=ports)

        #TODO: wait for pg to start
        time.sleep(10)

        courthouse_pid = start_courthouse()

        time.sleep(5)

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


def run_tests():
    driver = webdriver.Chrome()
    driver.get("http://localhost:9191/admin")
    driver.implicitly_wait(10)

if __name__ == '__main__':
    main()
