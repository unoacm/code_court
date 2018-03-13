#!/usr/bin/env python

import argparse
import logging
import os
import shutil
import signal
import stat
import subprocess
import sys
import time
import traceback
import uuid

from os import path

import docker
import requests

from requests.auth import HTTPBasicAuth

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s: %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")

SCRIPT_DIR = path.dirname(path.realpath(__file__))

EXECUTOR_IMAGE_NAME = "code-court-executor"
SHARED_DATA_DIR = path.join(SCRIPT_DIR, "share_data")

RUN_TIMEOUT = 5
CPU_PERIOD = 500000
MEM_LIMIT = "128m"
PID_LIMIT = 50
MEM_SWAPPINESS = 0
CONTAINER_USER = "user"
OUTPUT_LIMIT = 100000  # chars
WAIT_SECONDS = 5


class Executor:
    def __init__(self, conf):
        self.writ = None
        self.conf = conf
        self.client = docker.from_env()

    def start(self):
        while True:
            self._run()

    def _run(self):
        try:
            self.writ = self.get_writ()
            if not self.writ:
                time.sleep(WAIT_SECONDS)
            else:
                self.handle_writ()
        except KeyboardInterrupt:
            logging.info("Exiting")
            if self.writ:
                self.return_writ_without_output()
            sys.exit(0)
        except Exception:
            logging.exception("Uncaught exception, exiting")
            sys.exit(1)

    def handle_writ(self):
        logging.info("Executing writ (id: %s, lang: %s)", self.writ.run_id, self.writ.language)

        signal.signal(signal.SIGALRM, raise_timeout)
        signal.alarm(RUN_TIMEOUT)

        container = None
        try:
            if self.conf['insecure']:
                out = self.insecure_run_program()
            else:
                out = self.docker_run_program()

            signal.alarm(0)
        except TimedOutException:
            logging.info("Timed out writ %s", self.writ.run_id)
            self.submit_writ("Error: Timed out", RunState.TIMED_OUT)
        except OutputLimitExceeded:
            logging.info("Output limit exceeded on writ %s", self.writ.run_id)
            self.submit_writ("Error: Output limit exceeded", RunState.OUTPUT_LIMIT_EXCEEDED)
        except NoOutputException:
            logging.info("No output given from writ %s", self.writ.run_id)
            self.submit_writ("", RunState.NO_OUTPUT)
        except docker.errors.APIError:
            self.return_writ_without_output()
            traceback.print_exc()
        else:
            self.submit_writ(out, RunState.EXECUTED)
        finally:
            signal.alarm(0)
            if container:
                container.remove(force=True)
            try:
                shutil.rmtree(self.writ.shared_data_dir)
            except FileNotFoundError:
                pass

            self.writ = None

    def create_share_files(self, share_folder, runner_str, input_str, program_str):
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

    def get_writ(self):
        try:
            r = requests.get(
                self.conf['writ_url'],
                auth=HTTPBasicAuth(self.conf['email'], self.conf['password'])
            )
        except Exception:
            logging.exception("Failed to connect to courthouse")
            return None

        if r.status_code != 200:
            return None

        return Writ.from_json(r.json())

    def submit_writ(self, out, state):
        logging.info("Submitting writ %s, state: %s", self.writ.run_id, state)
        try:
            r = requests.post(
                self.conf['submit_url'].format(self.writ.run_id),
                json={"output": out, "state": state},
                auth=HTTPBasicAuth(self.conf['email'], self.conf['password'])
            )

            if r.status_code != 200:
                logging.error("Failed to submit writ, code: %s, response: %s", r.status_code, r.text)

        except requests.exceptions.ConnectionError:
            logging.exception("Failed to submit writ")
            try:
                self.return_writ_without_output()
            except Exception:
                logging.exception("Failed to return writ")

        self.current_writ = None

    def return_writ_without_output(self):
        logging.info("Returning writ without output: %s", self.writ.run_id)

        url = self.conf['return_url'] + "/" + str(self.writ.run_id)
        try:
            requests.post(
                url,
                auth=HTTPBasicAuth(self.conf['email'], self.conf['password'])
            )
        except requests.exceptions.ConnectionError:
            logging.exception("Failed to return writ")

    def insecure_run_program(self):
        container_shared_data_dir = self.writ.shared_data_dir

        runner_str = self.writ.run_script
        runner_str = runner_str.replace("$input_file", path.join(container_shared_data_dir, "input"))
        runner_str = runner_str.replace("$program_file", path.join(container_shared_data_dir, "program"))
        runner_str = runner_str.replace("$scratch_dir", container_shared_data_dir)

        os.makedirs(container_shared_data_dir)
        self.create_share_files(
            container_shared_data_dir,
            runner_str,
            self.writ.input,
            self.writ.source_code,
        )

        runner_file = path.join(container_shared_data_dir, "runner")
        out = subprocess.check_output(
            [runner_file],
            shell=True,
            stderr=subprocess.STDOUT
        ).decode('utf-8')
        if len(out) > OUTPUT_LIMIT:
            raise OutputLimitExceeded()

        if len(out) == 0:
            raise NoOutputException()

        return out

    def docker_run_program(self):
        container_shared_data_dir = self.writ.shared_data_dir

        runner_str = self.writ.run_script
        runner_str = runner_str.replace("$input_file", "/share/input")
        runner_str = runner_str.replace("$program_file", "/share/program")
        runner_str = runner_str.replace("$scratch_dir", "/scratch")

        os.makedirs(container_shared_data_dir)
        self.create_share_files(
            container_shared_data_dir,
            runner_str,
            self.writ.input,
            self.writ.source_code
        )
        shared_volumes = {
            container_shared_data_dir: {
                "bind": "/share",
                "mode": "ro"
            }
        }
        container = self.client.containers.run(EXECUTOR_IMAGE_NAME,
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

        if rolling_size == 0:
            raise NoOutputException()

        return "".join(out)


class Writ:
    def __init__(self, source_code, run_script, input, run_id, return_url, language):
        self.source_code = source_code
        self.run_script = run_script
        self.input = input
        self.run_id = run_id
        self.return_url = return_url
        self.language = language

        self.container_ident = "{}-{}-{}".format(self.run_id, self.language, str(uuid.uuid4()))
        self.shared_data_dir = path.join(SHARED_DATA_DIR, self.container_ident)

    @staticmethod
    def from_json(writ_json):
        if writ_json.get('status') == 'unavailable':
            return None

        source_code = writ_json.get('source_code')
        run_script = writ_json.get('run_script')
        input = writ_json.get('input')
        run_id = writ_json.get('run_id')
        return_url = writ_json.get('return_url')
        language = writ_json.get('language')

        if (
                source_code is None or
                run_script is None or
                input is None or
                run_id is None or
                return_url is None or
                language is None):
            logging.error("Received invalid writ: %s", writ_json)
            return None

        return Writ(
            source_code=source_code,
            run_script=run_script,
            input=input,
            run_id=run_id,
            return_url=return_url,
            language=language,
        )


def get_conf():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '-i',
        '--insecure',
        action='store_true',
        help='executes writs locally without docker in an insecure manner',
    )
    parser.add_argument(
        '-u',
        '--url',
        default="http://localhost:9191",
        help='the courthouse url',
    )
    parser.add_argument(
        '-e',
        '--email',
        default='exec@example.org',
        help='the email for the executor user',
    )
    parser.add_argument(
        '-p',
        '--password',
        default='epass',
        help='the password for the executor user',
    )

    args = parser.parse_args()

    conf = vars(args)  # turn args into dict
    conf['writ_url'] = "{}/api/get-writ".format(conf['url'])
    conf['submit_url'] = "{}/api/submit-writ/{{}}".format(conf['url'])
    conf['return_url'] = "{}/api/return-without-run".format(conf['url'])
    return conf


class OutputLimitExceeded(Exception):
    pass


class NoOutputException(Exception):
    pass


class TimedOutException(Exception):
    pass


def raise_timeout(signum, frame):
    raise TimedOutException()


class RunState:
    CONTEST_HAS_NOT_BEGUN = "ContestHasNotBegun"
    CONTEST_ENDED = "ContestEnded"
    SUCCESSFUL = "Successful"
    FAILED = "Failed"
    EXECUTED = "Executed"
    JUDGING = "Judging"
    NO_OUTPUT = "NoOutput"
    TIMED_OUT = "TimedOut"
    OUTPUT_LIMIT_EXCEEDED = "OutputLimitExceeded"


if __name__ == '__main__':
    Executor(get_conf()).start()
