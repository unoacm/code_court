from base_test import BaseTest

import model
import util
from database import db_session


class ModelsTestCase(BaseTest):
    """
    Contains tests for the database model
    """

    def test_language(self):
        """test the language table"""
        LANG_ARGS = {
            "name": "fakelang",
            "syntax_mode": "clike",
            "is_enabled": True,
            "run_script": "#!/bin/bash\nfakelang $1",
        }

        # create and add python lang
        lang = model.Language(**LANG_ARGS)
        db_session.add(lang)
        db_session.commit()

        # fetch lang
        results = model.Language.query.filter_by(name=LANG_ARGS["name"]).all()

        self.assertEqual(len(results), 1)

    def test_user(self):
        """test the user table"""
        USER_ARGS = {
            "username": "testuser",
            "name": "Test A. B. User",
            "password": "1231i411das9d8as9ds8as9d8a9da09sd8a0fsdasdasdasdaskjdasdj1j2k31jklj12k312k3j21k",
            "creation_time": util.str_to_dt("2017-01-01T12:12:00Z"),
            "misc_data": '{"teacher": "Cavanaugh"}',
        }

        # create and add user
        user = model.User(**USER_ARGS)
        db_session.add(user)
        db_session.commit()

        # fetch user
        results = model.User.query.filter_by(username=USER_ARGS["username"]).all()

        self.assertEqual(len(results), 1)

    def test_contest(self):
        """test the contest table"""
        CONTEST_ARGS = {
            "name": "1620 bracket",
            "activate_time": util.str_to_dt("2017-01-25T10:45:00Z"),
            "start_time": util.str_to_dt("2017-01-25T11:00:00Z"),
            "freeze_time": util.str_to_dt("2017-01-25T16:00:00Z"),
            "end_time": util.str_to_dt("2017-01-25T16:45:00Z"),
            "deactivate_time": util.str_to_dt("2017-01-26T10:45:00Z"),
            "is_public": True,
        }
        user_args, user = get_user()
        problem_args, problem = get_problem()

        # create and add contest
        contest = model.Contest(**CONTEST_ARGS)
        contest.users.append(user)
        contest.problems.append(problem)

        db_session.add(contest)
        db_session.commit()

        # fetch contest
        results = model.Contest.query.filter_by(name=CONTEST_ARGS["name"]).all()

        self.assertEqual(len(results), 1)

    def test_configuration(self):
        """test the configuration table"""
        CONF_ARGS = {
            "key": "use_strict_comparison",
            "val": "True",
            "valType": "bool",
            "category": "admin",
        }

        # create and add contest
        conf_type = model.Configuration(**CONF_ARGS)
        db_session.add(conf_type)
        db_session.commit()

        # fetch contest
        results = model.Configuration.query.filter_by(key=CONF_ARGS["key"]).all()

        self.assertEqual(len(results), 1)

    def test_problem_type(self):
        """test the problem_type table"""
        PROBLEM_TYPE_ARGS = {
            "name": "input/output",
            "eval_script": "#!/bin/bash\nexit 0",
        }

        # create and add contest
        problem_type = model.ProblemType(**PROBLEM_TYPE_ARGS)
        db_session.add(problem_type)
        db_session.commit()

        # fetch contest
        results = model.ProblemType.query.filter_by(
            name=PROBLEM_TYPE_ARGS["name"]
        ).all()

        self.assertEqual(len(results), 1)

    def test_problem(self):
        """test the problem table"""
        # add problem type
        PROBLEM_TYPE_ARGS = {
            "name": "input/output",
            "eval_script": "#!/bin/bash\nexit 0",
        }
        problem_type = model.ProblemType(**PROBLEM_TYPE_ARGS)
        db_session.add(problem_type)
        db_session.commit()

        PROBLEM_ARGS = {
            "problem_type": problem_type,
            "slug": "ioprob",
            "name": "The Input/Output Problem",
            "problem_statement": "Print the string 'Hello, World!' n times",
            "sample_input": "3",
            "sample_output": "Hello, World!Hello, World!Hello, World!",
            "secret_input": "4",
            "secret_output": "Hello, World!Hello, World!Hello, World!Hello, World!",
        }

        # create and add contest
        problem = model.Problem(**PROBLEM_ARGS)
        db_session.add(problem)
        db_session.commit()

        # fetch contest
        results = model.Problem.query.filter_by(name=PROBLEM_ARGS["name"]).all()

        self.assertEqual(len(results), 1)

    def test_saved_code(self):
        """test the saved_code table"""
        contest_args, contest = get_contest()
        problem_args, problem = get_problem()
        user_args, user = get_user()
        language_args, language = get_language()

        SAVED_CODE_ARGS = {
            "contest": contest,
            "problem": problem,
            "user": user,
            "language": language,
            "source_code": "print('hello')",
            "last_updated_time": util.str_to_dt("2017-01-26T10:45:00Z"),
        }
        saved_code = model.SavedCode(**SAVED_CODE_ARGS)
        db_session.add(saved_code)
        db_session.commit()

    def test_run(self):
        """test the run table"""
        contest_args, contest = get_contest()
        problem_args, problem = get_problem()
        user_args, user = get_user()
        language_args, language = get_language()

        RUN_ARGS = {
            "user": user,
            "contest": contest,
            "language": language,
            "problem": problem,
            "submit_time": util.str_to_dt("2017-01-26T10:45:00Z"),
            "source_code": "print('hello'*input())",
            "run_input": "5",
            "correct_output": "hellohellohellohellohello",
            "is_submission": True,
        }
        run = model.Run(**RUN_ARGS)
        db_session.add(run)
        db_session.commit()

    def test_clarification(self):
        """test the clarification table"""
        contest_args, contest = get_contest()
        problem_args, problem = get_problem()
        user_args, user = get_user()

        CLARIFICATION_ARGS = {
            "problem": problem,
            "initiating_user": user,
            "subject": "Test subject",
            "contents": "What is this thing?",
            "is_public": False,
        }
        clarification = model.Clarification(**CLARIFICATION_ARGS)
        db_session.add(clarification)
        db_session.commit()

        results = model.Clarification.query.filter_by(
            subject=CLARIFICATION_ARGS["subject"]
        ).all()

        self.assertEqual(len(results), 1)

    def test_user_role(self):
        """test the user_role table"""
        USER_ROLE_ARGS = {"name": "admin"}
        user_role = model.UserRole(**USER_ROLE_ARGS)
        db_session.add(user_role)
        db_session.commit()


def get_problem_type():
    """returns a test ProblemType"""
    PROBLEM_TYPE_ARGS = {"name": "input/output", "eval_script": "#!/bin/bash\nexit 0"}
    problem_type = model.ProblemType(**PROBLEM_TYPE_ARGS)
    db_session.add(problem_type)
    db_session.commit()

    return PROBLEM_TYPE_ARGS, problem_type


def get_problem():
    """returns a test Problem"""
    problem_type_args, problem_type = get_problem_type()
    PROBLEM_ARGS = {
        "problem_type": problem_type,
        "slug": "ioprob",
        "name": "The Input/Output Problem",
        "problem_statement": "Print the string 'Hello, World!' n times",
        "sample_input": "3",
        "sample_output": "Hello, World!Hello, World!Hello, World!",
        "secret_input": "4",
        "secret_output": "Hello, World!Hello, World!Hello, World!Hello, World!",
    }

    problem = model.Problem(**PROBLEM_ARGS)
    db_session.add(problem)
    db_session.commit()

    return PROBLEM_ARGS, problem


def get_language():
    """returns a test Language"""
    LANG_ARGS = {
        "name": "fakelang",
        "syntax_mode": "clike",
        "is_enabled": True,
        "run_script": "#!/bin/bash\nfakelang $1",
    }

    # create and add python lang
    lang = model.Language(**LANG_ARGS)
    db_session.add(lang)
    db_session.commit()

    return LANG_ARGS, lang


def get_user():
    """returns a test user"""
    USER_ARGS = {
        "username": "testuser",
        "name": "Test A. B. User",
        "password": "1231i411das9d8as9ds8as9d8a9da09sd8a0fsdasdasdasdaskjdasdj1j2k31jklj12k312k3j21k",
        "creation_time": util.str_to_dt("2017-01-01T12:12:00Z"),
        "misc_data": '{"teacher": "Cavanaugh"}',
    }

    # create and add user
    user = model.User(**USER_ARGS)
    db_session.add(user)
    db_session.commit()

    return USER_ARGS, user


def get_contest():
    """returns a test contest"""
    CONTEST_ARGS = {
        "name": "1620 bracket",
        "activate_time": util.str_to_dt("2017-01-25T10:45:00Z"),
        "start_time": util.str_to_dt("2017-01-25T11:00:00Z"),
        "freeze_time": util.str_to_dt("2017-01-25T16:00:00Z"),
        "end_time": util.str_to_dt("2017-01-25T16:45:00Z"),
        "deactivate_time": util.str_to_dt("2017-01-26T10:45:00Z"),
        "is_public": True,
    }

    # create and add contest
    contest = model.Contest(**CONTEST_ARGS)
    db_session.add(contest)
    db_session.commit()

    return CONTEST_ARGS, contest
