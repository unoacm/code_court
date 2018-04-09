#!/usr/bin/env python3

import logging
import random
import sys
import threading
import time

from urllib.parse import urljoin

import requests

BASE_URL = "http://localhost:9191/api/"

logging.basicConfig(level=logging.INFO)

class LoadTester:
    def run_clients(self, n=5):
        for i in range(n):
            print("Starting user #{}".format(i))
            FakeUser().start()
            time.sleep(.5)

        while True:
            time.sleep(1)


class FakeUser:
    PROBLEMS_INTERVAL = 5
    SCORES_INTERVAL = 30
    CONTEST_INTERVAL = 120
    SUBMIT_RUN_INTERVAL = 240

    def __init__(self):
        self.email, self.password = self.create_user()
        self.login_token = self.get_login_token(self.email, self.password)
        self.user_info = self.get_user_info()
        self.contest_info = self.get_contest_info()

    def start(self):
        def _scores():
            time.sleep(random.uniform(0, self.SCORES_INTERVAL))
            while True:
                self.get_scores()
                time.sleep(self.SCORES_INTERVAL)
        threading.Thread(target=_scores).start()

        def _problems():
            time.sleep(random.uniform(0, self.PROBLEMS_INTERVAL))
            while True:
                self.get_problems()
                time.sleep(self.PROBLEMS_INTERVAL)
        threading.Thread(target=_problems).start()

        def _contest():
            time.sleep(random.uniform(0, self.CONTEST_INTERVAL))
            while True:
                self.get_contest_info()
                time.sleep(self.CONTEST_INTERVAL)
        threading.Thread(target=_contest).start()

        def _runs():
            time.sleep(random.uniform(0, self.SUBMIT_RUN_INTERVAL))
            while True:
                self.submit_run()
                time.sleep(self.SUBMIT_RUN_INTERVAL)
        threading.Thread(target=_runs).start()

    def _get(self, url):
        start_time = millis()
        headers = {
            "Authorization": "Bearer {}".format(self.login_token)
        }
        try:
            r = requests.get(url, headers=headers)
        except requests.exceptions.ConnectionError:
            logging.error("Connection error while getting %s", url)
            return None

        if r.status_code != 200:
            logging.error("Error %s while getting %s: %s", r.status_code, url, r.text)

        _log_timing(url, start_time)

        return r

    def _post(self, url, json, login_token=None):
        start_time = millis()
        chosen_login_token = login_token if login_token else self.login_token
        headers = {
            "Authorization": "Bearer {}".format(chosen_login_token)
        }

        try:
            r = requests.post(url, json=json, headers=headers)
        except requests.exceptions.ConnectionError:
            logging.error("Connection error while posting %s", url)
            return None

        if r.status_code != 200:
            logging.error("Error %s while posting %s: %s", r.status_code, url, r.text)

        _log_timing(url, start_time)

        return r

    def _get_api(self, part):
        url = urljoin(BASE_URL, part)
        r =  self._get(url)
        if r:
            return r.json()
        else:
            return None

    def _post_api(self, part, json, login_token=None):
        url = urljoin(BASE_URL, part)
        r = self._post(url, json, login_token)
        if r:
            return r.json()
        else:
            return None

    def loop(self):
        while True:
            self.get_scores()
            self.get_problems()
            self.submit_run()
            time.sleep(1)

    def submit_run(self):
        correct_solution = "print('Hello, World!')"
        incorrect_solution = "for x in range(10000):\n\tprint(x)"
        data = dict(
            lang="python",
            problem_slug="hello-world",
            source_code=random.choice([correct_solution, incorrect_solution]),
            is_submission=False,
            user_test_input="",
        )
        self._post_api("submit-run", data)

    def get_scores(self):
        contest_id = self.contest_info['id']
        return self._get_api("scores/{}".format(contest_id))

    def get_problems(self):
        user_id = self.user_info['id']
        return self._get_api("problems/{}".format(user_id))

    def get_contest_info(self):
        return self._get_api("get-contest-info")

    def get_user_info(self):
        return self._get_api("current-user")

    def create_user(self):
        admin_login_token = self.get_login_token("admin@example.org", "pass")
        user_id = random.randint(1000, 1_000_000)
        data = dict(
            email="{}@example.org".format(user_id),
            name=user_id,
            password="pass",
            username=user_id,
            contest_name="test_contest",
        )
        self._post_api("make-defendant-user", data, login_token=admin_login_token)
        return (data['email'], data['password'])

    def get_login_token(self, email, password):
        url = urljoin(BASE_URL, "login")
        data = dict(
            email=email,
            password=password,
        )

        r = requests.post(url, json=data)
        if r.status_code != 200:
            raise Exception("Failed login request")

        return r.json().get("access_token")


def millis():
    return int(round(time.time() * 1000))


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def _log_timing(url, start_time):
    time_taken = millis() - start_time
    time_taken_str = "{}ms".format(time_taken)
    if time_taken > 1000:
        time_taken_str = bcolors.FAIL + time_taken_str + bcolors.ENDC
    elif time_taken > 100:
        time_taken_str = bcolors.WARNING + time_taken_str + bcolors.ENDC
    logging.info("Request to %-50s took %s", url, time_taken_str)


if __name__ == '__main__':
    try:
        load_tester = LoadTester()
        load_tester.run_clients(int(sys.argv[1]))
    except KeyboardInterrupt:
        sys.exit(0)
