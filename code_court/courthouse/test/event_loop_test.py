import datetime

from event_loop import reset_overdue_runs
import web
from base_test import BaseTest

from web import model


class EventLoopTestCase(BaseTest):
    """
    Contains tests for the event loop
    """
    def test_reset_overdue_run(self):
        """tests if an overdue run gets reset"""
        EXECUTOR_TIMEOUT_MINS = 5

        contest_args, contest = get_contest()
        problem_args, problem = get_problem()
        user_args, user = get_user()
        language_args, language = get_language()

        RUN_ARGS = {
            "user": user,
            "contest": contest,
            "language": language,
            "problem": problem,
            "submit_time": model.str_to_dt('2017-01-26T10:45Z'),
            "source_code": "print('hello'*input())",
            "run_input": "5",
            "correct_output": "hellohellohellohellohello",
            "is_submission": True,
        }
        run = model.Run(**RUN_ARGS)
        run.started_execing_time = datetime.datetime.utcnow() - datetime.timedelta(minutes=EXECUTOR_TIMEOUT_MINS+1)
        run.finished_execing_time = None
        model.db.session.add(run)
        model.db.session.commit()

        reset_overdue_runs()

        queried_run = model.Run.query.scalar()

        self.assertEqual(queried_run.started_execing_time, None)

    def test_do_not_reset_not_overdue_run(self):
        """tests if an overdue run gets reset"""
        EXECUTOR_TIMEOUT_MINS = 5

        contest_args, contest = get_contest()
        problem_args, problem = get_problem()
        user_args, user = get_user()
        language_args, language = get_language()

        RUN_ARGS = {
            "user": user,
            "contest": contest,
            "language": language,
            "problem": problem,
            "submit_time": model.str_to_dt('2017-01-26T10:45Z'),
            "source_code": "print('hello'*input())",
            "run_input": "5",
            "correct_output": "hellohellohellohellohello",
            "is_submission": True,
        }
        run = model.Run(**RUN_ARGS)
        run.started_execing_time = datetime.datetime.utcnow() - datetime.timedelta(minutes=EXECUTOR_TIMEOUT_MINS-1)
        run.finished_execing_time = None
        model.db.session.add(run)
        model.db.session.commit()

        reset_overdue_runs()

        queried_run = model.Run.query.scalar()

        self.assertEqual(queried_run.started_execing_time, run.started_execing_time)

def get_problem_type():
    """returns a test ProblemType"""
    PROBLEM_TYPE_ARGS = {
        "name": "input/output",
        "eval_script": "#!/bin/bash\nexit 0",
    }
    problem_type = model.ProblemType(**PROBLEM_TYPE_ARGS)
    model.db.session.add(problem_type)
    model.db.session.commit()

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
    model.db.session.add(problem)
    model.db.session.commit()

    return PROBLEM_ARGS, problem

def get_language():
    """returns a test Language"""
    LANG_ARGS = {
        "name": "fakelang",
        "is_enabled": True,
        "run_script": "#!/bin/bash\nfakelang $1",
    }

    # create and add python lang
    lang = model.Language(**LANG_ARGS)
    model.db.session.add(lang)
    model.db.session.commit()

    return LANG_ARGS, lang

def get_user():
    """returns a test user"""
    USER_ARGS = {
        "email": "testuser@example.org",
        "name": "Test A. B. User",
        "password": "1231i411das9d8as9ds8as9d8a9da09sd8a0fsdasdasdasdaskjdasdj1j2k31jklj12k312k3j21k",
        "creation_time": model.str_to_dt("2017-01-01T12:12Z"),
        "misc_data": '{"teacher": "Cavanaugh"}',
    }

    # create and add user
    user = model.User(**USER_ARGS)
    model.db.session.add(user)
    model.db.session.commit()

    return USER_ARGS, user

def get_contest():
    """returns a test contest"""
    CONTEST_ARGS = {
        "name": "1620 bracket",
        "activate_time": model.str_to_dt('2017-01-25T10:45Z'),
        "start_time": model.str_to_dt('2017-01-25T11:00Z'),
        "freeze_time": model.str_to_dt('2017-01-25T16:00Z'),
        "end_time": model.str_to_dt('2017-01-25T16:45Z'),
        "deactivate_time": model.str_to_dt('2017-01-26T10:45Z'),
        "is_public": True,
    }

    # create and add contest
    contest = model.Contest(**CONTEST_ARGS)
    model.db.session.add(contest)
    model.db.session.commit()

    return CONTEST_ARGS, contest

