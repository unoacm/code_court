import json
import os
import tempfile
import unittest

from base64 import b64encode

import web

from web import app, model


class APITestCase(unittest.TestCase):
    """
    Contains tests for the api blueprint
    """
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"
        app.config['TESTING'] = True
        app.app_context().push()
        self.app = app.test_client()
        with app.app_context():
            web.setup_database(app)

    def test_executioner_deny(self):
        """Tests that authentication is needed to request writs"""
        setup_contest()

        # note: no basicauth
        rv = self.app.get('/api/get-writ')
        self.assertEqual(rv.status_code, 401)

        wrong_auth_headers = {
            'Authorization': 'Basic %s' % b64encode(b"wronguser@example.com:wrongpass").decode("ascii")
        }
        rv = self.app.get('/api/get-writ', headers=wrong_auth_headers)
        self.assertEqual(rv.status_code, 401)

    def test_executioner_api(self):
        """Tests the api for requesting and submitting writs by the api"""
        setup_contest()

        auth_headers = {
            'Authorization': 'Basic %s' % b64encode(b"testexec@example.com:epass").decode("ascii")
        }

        # get writ
        rv = self.app.get('/api/get-writ', headers=auth_headers)
        self.assertEqual(rv.status_code, 200)
        writ_data = json.loads(rv.data.decode("utf-8"))

        self.assertIn('source_code', writ_data)
        self.assertIn('language', writ_data)
        self.assertIn('run_script', writ_data)
        self.assertIn('return_url', writ_data)
        self.assertEqual(writ_data['status'], 'found')

        # submit writ
        run_id = writ_data['return_url'].split("/")[-1]
        submit_data = {'output': 'run_output'}
        rv = self.app.post('/api/submit-writ/{}'.format(run_id),
                           headers=auth_headers, data=json.dumps(submit_data),
                           content_type='application/json')
        self.assertEqual(rv.status_code, 200)

        # verify no more writs
        rv = self.app.get('/api/get-writ', headers=auth_headers)
        self.assertEqual(rv.status_code, 404)

    def tearDown(self):
        model.db.drop_all()

def setup_contest():
    roles = {x.id: x for x in model.UserRole.query.all()}
    test_contestant = model.User("testuser@xample.com", "Test User", "pass", user_roles=[roles['defendant']])
    test_executioner = model.User("testexec@example.com", "Test Executioner", "epass", user_roles=[roles['executioner']])
    test_contest = model.Contest("test_contest", model.str_to_dt("2017-02-05T22:04"),
                                 model.str_to_dt("2030-01-01T11:11"), True)
    io_problem_type = model.ProblemType.query.filter_by(name="input-output").one()
    test_problem = model.Problem(io_problem_type, "fizzbuzz", "## FizzBuzz\nPerform fizzbuzz up to the given number",
                                 "3", "1\n2\nFizz",
                                 "15", "1\n2\nFizz\n4\nBuzz\nFizz\n7\n8\n9\nBuzz\n11\nFizz\n13\n14\nFizzBuzz\n")
    test_contest.problems.append(test_problem)
    test_contest.users.append(test_contestant)

    python = model.Language.query.filter_by(name="python").one()
    test_run = model.Run(test_contestant, test_contest, python, test_problem, model.str_to_dt("2017-02-05T23:00"),
                         'import sys\nn=raw_input()\nfor i in range(1, n+1): print("Fizz"*(i%3==0)+"Buzz"*(i%5==0) or i)',
                         test_problem.secret_input, True)

    model.db.session.add_all([test_executioner, test_contestant, test_contest, test_problem, test_run])
    model.db.session.commit()

if __name__ == '__main__':
    unittest.main()
