import json

from base64 import b64encode

from base_test import BaseTest

import model
import util
from database import db_session


class APITestCase(BaseTest):
    """
    Contains tests for the api blueprint
    """

    def test_executioner_deny(self):
        """Tests that authentication is needed to request writs"""
        setup_contest()

        # note: no basicauth
        rv = self.app.get("/api/get-writ")
        self.assertEqual(rv.status_code, 401)

        wrong_auth_headers = {
            "Authorization": "Basic %s"
            % b64encode(b"wronguser:wrongpass").decode("ascii")
        }
        rv = self.app.get("/api/get-writ", headers=wrong_auth_headers)
        self.assertEqual(rv.status_code, 401)

    def test_executioner_api(self):
        """Tests the api for requesting and submitting writs by the api"""
        setup_contest()

        auth_headers = {
            "Authorization": "Basic %s" % b64encode(b"testexec:epass").decode("ascii")
        }

        # get writ
        rv = self.app.get("/api/get-writ", headers=auth_headers)
        self.assertEqual(rv.status_code, 200)
        writ_data = json.loads(rv.data.decode("utf-8"))

        self.assertIn("source_code", writ_data)
        self.assertIn("language", writ_data)
        self.assertIn("run_script", writ_data)
        self.assertIn("return_url", writ_data)
        self.assertIn("run_id", writ_data)
        self.assertEqual(writ_data["status"], "found")

        # verify the run has started but has not finished execing
        run = model.Run.query.filter_by(id=writ_data["run_id"]).one()
        self.assertNotEqual(run.started_execing_time, None)
        self.assertEqual(run.finished_execing_time, None)

        # verify no more writs
        # There is the language version run, so get-writ is called twice
        self.app.get("/api/get-writ", headers=auth_headers)
        rv = self.app.get("/api/get-writ", headers=auth_headers)
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(json.loads(rv.data.decode("utf-8"))["status"], "unavailable")

        # give back writ
        rv = self.app.post(
            "/api/return-without-run/{}".format(writ_data["run_id"]),
            headers=auth_headers,
        )
        self.assertEqual(rv.status_code, 200)

        # get writ again
        rv = self.app.get("/api/get-writ", headers=auth_headers)
        self.assertEqual(rv.status_code, 200)
        writ_data = json.loads(rv.data.decode("utf-8"))

        # submit writ
        submit_data = {"output": "run_output"}
        rv = self.app.post(
            "/api/submit-writ/{}".format(writ_data["run_id"]),
            headers=auth_headers,
            data=json.dumps(submit_data),
            content_type="application/json",
        )
        self.assertEqual(rv.status_code, 200)

        # verify no more writs
        rv = self.app.get("/api/get-writ", headers=auth_headers)
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(json.loads(rv.data.decode("utf-8"))["status"], "unavailable")

    def test_rejudging(self):
        """Tests rejudging endpoint"""
        # A version run is being added on db startup
        for run in model.Run.query.all():
            db_session.delete(run)
        db_session.commit()

        setup_contest()
        self.login("admin", "pass")

        test_run = model.Run.query.first()

        self._judge_writ()

        self.assertIsNotNone(test_run.started_execing_time)
        self.assertIsNotNone(test_run.finished_execing_time)
        self.assertIsNotNone(test_run.run_output)

        rv = self.app.get(
            "/admin/runs/{}/rejudge".format(test_run.id), follow_redirects=True
        )
        self.assertEqual(rv.status_code, 200)

        self.assertIsNone(test_run.started_execing_time)
        self.assertIsNone(test_run.finished_execing_time)
        self.assertIsNone(test_run.run_output)

    def _judge_writ(self):
        auth_headers = {
            "Authorization": "Basic %s" % b64encode(b"testexec:epass").decode("ascii")
        }

        rv = self.app.get("/api/get-writ", headers=auth_headers)
        writ_data = json.loads(rv.data.decode("utf-8"))

        self.app.post(
            "/api/submit-writ/{}".format(writ_data["run_id"]),
            headers=auth_headers,
            data=json.dumps({"output": "run_output"}),
            content_type="application/json",
        )

    def test_submit_run(self):
        """Tests the run submit endpoint"""
        setup_contest()
        token = self.get_jwt_token("testuser", "pass")

        data = dict(
            lang="python",
            problem_slug="fizzbuzz",
            source_code="adasdiajdasdjasldjaslkasd",
            is_submission=True,
            user_test_input=None,
        )

        rv = self.post_json("/api/submit-run", data, auth_token=token)
        self.assertEqual(rv.status_code, 200)

    def test_get_problems(self):
        """Tests the /api/problems endpoint"""
        setup_contest()
        token = self.get_jwt_token("testuser", "pass")

        rv = self.jwt_get("/api/problems", auth_token=token)
        self.assertEqual(rv.status_code, 200)

        problems = json.loads(rv.data.decode("utf-8"))
        self.assertIn("fizzbuzz", problems)

        self.assertEqual(1, len(problems["fizzbuzz"]["runs"]))

    def test_get_current_user(self):
        """Tests the /api/current-user endpoint"""
        setup_contest()
        token = self.get_jwt_token("testuser", "pass")

        rv = self.jwt_get("/api/current-user", auth_token=token)
        self.assertEqual(rv.status_code, 200)

        user = json.loads(rv.data.decode("utf-8"))
        self.assertEqual(user.get("username"), "testuser")

    def test_get_contest_info(self):
        """Tests the /api/get-contest-info endpoint"""
        setup_contest()
        token = self.get_jwt_token("testuser", "pass")

        rv = self.jwt_get("/api/get-contest-info", auth_token=token)
        self.assertEqual(rv.status_code, 200)

        contest = json.loads(rv.data.decode("utf-8"))
        self.assertEqual(contest.get("name"), "test_contest")

    def test_signup(self):
        """Tests the /api/signup endpoint"""
        setup_contest()

        data = dict(
            username="signuptest",
            name="Signup Test",
            password="pass",
            password2="pass",
            contest_name="test_contest",
        )

        rv = self.post_json("/api/signup", data)
        self.assertEqual(rv.status_code, 200, rv.data)

        token = self.get_jwt_token(data["username"], data["password"])
        self.assertIsNotNone(token)

    def test_signup_with_extra_signup_fields(self):
        """Tests the /api/signup endpoint with extra signup fields"""
        setup_contest()
        util.set_configuration(
            "extra_signup_fields", json.dumps(["example_extra_field"])
        )

        data = dict(
            username="signuptest",
            name="Signup Test",
            password="pass",
            password2="pass",
            contest_name="test_contest",
            example_extra_field="asdf",
        )

        rv = self.post_json("/api/signup", data)
        self.assertEqual(rv.status_code, 200, rv.data)

        token = self.get_jwt_token(data["username"], data["password"])
        self.assertIsNotNone(token)

        user = model.User.query.filter_by(username=data["username"]).scalar()
        self.assertEqual(
            user.get_metadata_item("example_extra_field"), data["example_extra_field"]
        )

    def test_get_languages(self):
        """Tests the /api/languages endpoint"""
        setup_contest()

        num_langs = model.Language.query.count()

        rv = self.jwt_get("/api/languages")
        self.assertEqual(rv.status_code, 200)

        langs = json.loads(rv.data.decode("utf-8"))
        self.assertEqual(len(langs), num_langs)

    def test_get_clarifications(self):
        setup_contest()
        
        num_clars = model.Clarification.query.count()

        rv = self.jwt_get("/api/clarifications")
        self.assertEqual(rv.status_code, 200)

        clars = json.loads(rv.data.decode("utf-8"))
        self.assertEqual(len(clars), num_clars)

    def test_submit_clarification(self):
        """Tests the /api/submit_clarification endpoint"""
        setup_contest()
        token = self.get_jwt_token("testuser", "pass")

        data = dict(
            problem="fizzbuzz",
            initiating_user="testuser",
            subject="test",
            contents="halp",
            is_public=False
        )

        rv = self.post_json("/api/submit_clarification", data, auth_token=token)
        self.assertEqual(rv.status_code, 200, rv.data)

        clarification = model.Clarification.query.filter_by(subject="test").first()
        self.assertIsNotNone(clarification)

    def test_answer_clarification(self):
        """Tests the /api/answer_clarification endpoint"""
        setup_contest()

        data = dict(
            subject="test",
            problem="FizzBuzz",
            answer="solve"
        )

        rv = self.post_json("/api/answer_clarification", data)
        self.assertEqual(rv.status_code, 200, rv.data)

        clarification = model.Clarification.query.filter_by(subject="test").first()
        self.assertEqual("solve", clarification.answer)


def setup_contest():
    roles = {x.name: x for x in model.UserRole.query.all()}
    test_contestant = model.User(
        "testuser", "Test User", "pass", user_roles=[roles["defendant"]]
    )
    test_executioner = model.User(
        "testexec", "Test Executioner", "epass", user_roles=[roles["executioner"]]
    )
    test_contest = model.Contest(
        "test_contest",
        util.str_to_dt("2017-02-05T22:04:00Z"),
        util.str_to_dt("2030-01-01T11:11:00Z"),
        True,
    )
    io_problem_type = model.ProblemType.query.filter_by(name="input-output").one()
    test_problem = model.Problem(
        io_problem_type,
        "fizzbuzz",
        "FizzBuzz",
        "## FizzBuzz\nPerform fizzbuzz up to the given number",
        "3",
        "1\n2\nFizz",
        "15",
        "1\n2\nFizz\n4\nBuzz\nFizz\n7\n8\n9\nBuzz\n11\nFizz\n13\n14\nFizzBuzz\n",
    )
    test_contest.problems.append(test_problem)
    test_contest.users.append(test_contestant)

    python = model.Language.query.filter_by(name="python").one()
    test_run = model.Run(
        test_contestant,
        test_contest,
        python,
        test_problem,
        util.str_to_dt("2017-02-05T23:00:00Z"),
        'import sys\nn=raw_input()\nfor i in range(1, n+1): print("Fizz"*(i%3==0)+"Buzz"*(i%5==0) or i)',
        test_problem.secret_input,
        test_problem.secret_output,
        True,
    )

    test_clarification = model.Clarification(
            test_problem,
            test_contestant,
            "test",
            "help",
            False
    )

    db_session.add_all(
        [test_executioner, test_contestant, test_contest, test_problem, test_run, test_clarification]
    )
    db_session.commit()
