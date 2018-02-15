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
            time.sleep(5)

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
            while True:
                self.get_scores()
                time.sleep(self.SCORES_INTERVAL)
        threading.Thread(target=_scores).start()

        def _problems():
            while True:
                self.get_problems()
                time.sleep(self.PROBLEMS_INTERVAL)
        threading.Thread(target=_problems).start()

        def _contest():
            while True:
                self.get_contest_info()
                time.sleep(self.CONTEST_INTERVAL)
        threading.Thread(target=_contest).start()

        def _runs():
            while True:
                self.submit_run()
                time.sleep(self.SUBMIT_RUN_INTERVAL)
        threading.Thread(target=_runs).start()

    def _get(self, url):
        headers = {
            "Authorization": "Bearer {}".format(self.login_token)
        }
        r = requests.get(url, headers=headers)

        if r.status_code != 200:
            logging.error("Error %s while getting %s: %s", r.status_code, url, r.text)

        return r

    def _post(self, url, json, login_token=None):
        chosen_login_token  = login_token if login_token else self.login_token
        headers = {
            "Authorization": "Bearer {}".format(chosen_login_token)
        }
        r = requests.post(url, json=json, headers=headers)

        if r.status_code != 200:
            logging.error("Error %s while posting %s: %s", r.status_code, url, r.text)

        return r

    def _get_api(self, part):
        url = urljoin(BASE_URL, part)
        r =  self._get(url).json()
        return r

    def _post_api(self, part, json, login_token=None):
        url = urljoin(BASE_URL, part)
        r = self._post(url, json, login_token).json()
        return r

    def loop(self):
        while True:
            self.get_scores()
            self.get_problems()
            self.submit_run()
            time.sleep(1)

    def submit_run(self):
        logging.info("Submitting run")
        data = dict(
            lang="python",
            problem_slug="hello-world",
            source_code="print('hello world')",
            is_submission=False,
            user_test_input="",
        )
        self._post_api("submit-run", data)

    def get_scores(self):
        logging.info("Requesting scores")
        contest_id = self.contest_info['id']
        return self._get_api("scores/{}".format(contest_id))

    def get_problems(self):
        logging.info("Requesting problems")
        user_id = self.user_info['id']
        return self._get_api("problems/{}".format(user_id))

    def get_contest_info(self):
        logging.info("Requesting contest info")
        return self._get_api("get-contest-info")

    def get_user_info(self):
        logging.info("Requesting user info")
        return self._get_api("current-user")

    def create_user(self):
        logging.info("Creating user")
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
        logging.info("Requesting login token")
        url = urljoin(BASE_URL, "login")
        data = dict(
            email=email,
            password=password,
        )

        r = requests.post(url, json=data)
        if r.status_code != 200:
            raise Exception("Failed login request")

        return r.json().get("access_token")


if __name__ == '__main__':
    try:
        load_tester = LoadTester()
        load_tester.run_clients(int(sys.argv[1]))
    except KeyboardInterrupt:
        sys.exit(0)
