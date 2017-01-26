import datetime
import os
import tempfile
import unittest

import web

from web import app, model

def string_to_dt(s):
    return datetime.datetime.strptime(s, '%Y-%m-%dT%H:%M')

class ModelsTestCase(unittest.TestCase):
    """
    Contains tests for the database model
    """
    def setUp(self):
        self.db_fd, self.dbfile = tempfile.mkstemp()
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + self.dbfile
        app.config['TESTING'] = True
        app.app_context().push()
        self.app = app.test_client()
        with app.app_context():
            web.setup_database(app)

    def test_language(self):
        """test the language table"""
        LANG_ARGS = {
            "name": "python",
            "is_enabled": True,
            "run_script": "#!/bin/bash\npython $1",
        }

        # create and add python lang
        python = model.Language(**LANG_ARGS)
        model.db.session.add(python)
        model.db.session.commit()

        # fetch python lang
        results = model.Language.query.filter_by(name=LANG_ARGS['name']).all()

        self.assertEqual(len(results), 1)

    def test_user(self):
        """test the user table"""
        USER_ARGS = {
            "email": "testuser@example.com",
            "name": "Test A. B. User",
            "password": "1231i411das9d8as9ds8as9d8a9da09sd8a0fsdasdasdasdaskjdasdj1j2k31jklj12k312k3j21k",
            "creation_time": string_to_dt("2017-01-01T12:12"),
            "misc_data": '{"teacher": "Cavanaugh"}',
        }

        # create and add user
        user = model.User(**USER_ARGS)
        model.db.session.add(user)
        model.db.session.commit()

        # fetch user
        results = model.User.query.filter_by(email=USER_ARGS['email']).all()

        self.assertEqual(len(results), 1)

    def test_contest(self):
        """test the contest table"""
        CONTEST_ARGS = {
            "name": "1620 bracket",
            "activate_time": string_to_dt('2017-01-25T10:45'),
            "start_time": string_to_dt('2017-01-25T11:00'),
            "freeze_time": string_to_dt('2017-01-25T16:00'),
            "end_time": string_to_dt('2017-01-25T16:45'),
            "deactivate_time": string_to_dt('2017-01-26T10:45'),
            "is_public": True,
        }

        # create and add contest
        contest = model.Contest(**CONTEST_ARGS)
        model.db.session.add(contest)
        model.db.session.commit()

        # fetch contest
        results = model.Contest.query.filter_by(name=CONTEST_ARGS['name']).all()

        self.assertEqual(len(results), 1)

    def test_problem_type(self):
        """test the problem_type table"""
        PT_ARGS = {
            "name": "1620 bracket",
            "eval_script": "import sys; sys.exit(0)"
        }

        # create and add contest
        problem_type = model.ProblemType(**PT_ARGS)
        model.db.session.add(problem_type)
        model.db.session.commit()

        # fetch contest
        results = model.ProblemType.query.filter_by(name=PT_ARGS['name']).all()

        self.assertEqual(len(results), 1)

    def test_configuration(self):
        """test the configuration table"""
        CONF_ARGS = {
            "key": "use_strict_comparison",
            "val": "True",
            "valType": "bool",
        }

        # create and add contest
        conf_type = model.Configuration(**CONF_ARGS)
        model.db.session.add(conf_type)
        model.db.session.commit()

        # fetch contest
        results = model.Configuration.query.filter_by(key=CONF_ARGS['key']).all()

        self.assertEqual(len(results), 1)

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.dbfile)

if __name__ == '__main__':
    unittest.main()
