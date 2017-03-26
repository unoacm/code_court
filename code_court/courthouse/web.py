#!/usr/bin/env python3
"""
The entrypoint to the courthouse application
"""
import datetime
import logging
import os
import random
import textwrap

from logging.handlers import RotatingFileHandler
from logging import StreamHandler
from os import path

from flask import Flask, render_template

from flask_cors import CORS
from flask_debugtoolbar import DebugToolbarExtension
from flask_jwt_extended import JWTManager
from flask_login import LoginManager, current_user

import model
import util

from model import db

from views.main import main
from views.api import api
from views.admin.admin import admin
from views.admin.configurations import configurations
from views.admin.languages import languages
from views.admin.problems import problems
from views.admin.users import users
from views.admin.runs import runs
from views.admin.contests import contests
from views.defendant import defendant
from views.auth import auth

# turn down log level for werkzeug
wlog = logging.getLogger('werkzeug')
wlog.setLevel(logging.ERROR)

log_location = 'logs/code_court.log'

app = Flask(__name__)

def create_app():
    """
    Initializes the flask app object

    Returns:
        Flask: the initialized flask app
    """
    app = Flask(__name__)
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 86400 # 1 day

    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/code_court.db" #TODO: put this in config
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = False
    app.config['model'] = model
    app.config['SECRET_KEY'] = 'secret key1234' #TODO: put this in config
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=30)
    # app.debug = True

    # Add datetime to string filter to Jinja2
    # http://flask.pocoo.org/docs/0.12/templating/
    app.jinja_env.filters['dt_to_str'] = model.dt_to_str
    app.jinja_env.filters['dt_to_date_str'] = model.dt_to_date_str
    app.jinja_env.filters['dt_to_time_str'] = model.dt_to_time_str

    db.init_app(app)
    CORS(app)

    jwt = JWTManager(app)

    login_manager = LoginManager()
    login_manager.init_app(app)

    login_manager.login_view = "auth.login_view"

    toolbar = DebugToolbarExtension(app)

    @login_manager.user_loader
    def load_user(user_email):
        return model.User.query.filter_by(email=user_email).one()

    app.logger.setLevel(logging.DEBUG)

    app.register_blueprint(main, url_prefix='')
    app.register_blueprint(api, url_prefix='/api')
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(configurations, url_prefix='/admin/configurations')
    app.register_blueprint(languages, url_prefix='/admin/languages')
    app.register_blueprint(problems, url_prefix='/admin/problems')
    app.register_blueprint(users, url_prefix='/admin/users')
    app.register_blueprint(runs, url_prefix='/admin/runs')
    app.register_blueprint(contests, url_prefix='/admin/contests')
    app.register_blueprint(defendant, url_prefix='/defendant')
    app.register_blueprint(auth, url_prefix='')

    @app.context_processor
    def inject_user():
        return {
        }

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(401)
    @login_manager.unauthorized_handler
    def unauthorized(callback=None):
        if not current_user.is_authenticated:
            return render_template('auth/login.html'), 401
        return render_template('401.html'), 401

    return app

def setup_database(app):
    """Creates the database tables on initial startup"""
    with app.app_context():
        if not is_db_inited(app):
            app.logger.info("Creating db tables")
            db.create_all()
            db.session.commit()
            init_db(app)
            if not app.config['TESTING']:
                dev_init_db(app)

def is_db_inited(app):
    """Checks if the db is initialized

    Args:
        app: the flask app

    Returns:
        bool: True if the database has been initialized
    """
    with app.app_context():
        if not db.engine.dialect.has_table(db.engine, "user_role"):
            return False
        return model.UserRole.query.count() > 0

def init_db(app):
    """Performs the initial database setup for the application
    """
    with app.app_context():
        app.logger.info("Initializing db tables")

        model.db.session.add_all([model.UserRole("defendant"),
                                  model.UserRole("operator"),
                                  model.UserRole("judge"),
                                  model.UserRole("executioner")])

        # TODO: extract these out into a folder
        model.db.session.add_all([
            model.Language("python",
                     True,
                     textwrap.dedent('''#!/bin/bash
                                        cat $1 | python3 $2
                                        exit $?'''
            )),
            model.Language("python2",
                     True,
                     textwrap.dedent('''#!/bin/bash
                                        cat $1 | python2 $2
                                        exit $?'''
            )),
            model.Language("ruby",
                           True,
                           textwrap.dedent('''#!/bin/bash
                                              cat $1 | ruby $2
                                              exit $?'''
            ))])
        # model.db.session.add_all([model.Language("python", True, '#!/bin/bash\ncat $1 | python $2\nexit $?')])

        model.db.session.add_all([model.Configuration("strict_whitespace_diffing", "False", "bool"),
                                  model.Configuration("contestants_see_sample_output", "True", "bool")])

        model.db.session.add_all([model.ProblemType("input-output",
                                                    '#!/bin/bash\ntest "$1" = "$2"')])

        roles = {x.id: x for x in model.UserRole.query.all()}
        model.db.session.add(model.User("admin@example.org", "Admin", "pass", user_roles=[roles['operator']]))

        model.db.session.commit()

def dev_init_db(app):
    """Performs the initial database setup for the application
    """
    with app.app_context():
        app.logger.info("Initializing tables with dev data")
        roles = {x.id: x for x in model.UserRole.query.all()}

        model.db.session.add_all([model.User("exec@example.org", "Executioner", "epass", user_roles=[roles['executioner']]),
                                  model.User("super@example.org", "SuperUser", "pass", user_roles=list(roles.values()))])

        contestants = []
        names = ["Fred", "George", "Jenny", "Sam", "Jo", "Joe", "Sarah", "Ben", "Josiah", "Micah"]
        for i in range(1,11):
            test_contestant = model.User("testuser{}@example.org".format(i),
                                         names[i-1], "pass", user_roles=[roles['defendant']])
            model.db.session.add(test_contestant)
            contestants.append(test_contestant)


        # create test contest
        test_contest = model.Contest(name = "test_contest",
                                     start_time = model.str_to_dt("2017-02-05T22:04"),
                                     end_time = model.str_to_dt("2030-01-01T11:11"),
                                     is_public = True,
                                     activate_time = model.str_to_dt("2018-02-05T22:04"),
                                     freeze_time = model.str_to_dt("2019-02-05T22:04"),
                                     deactivate_time = model.str_to_dt("2031-02-05T22:04"))
        test_contest.users += contestants
        model.db.session.add(test_contest)

        io_problem_type = model.ProblemType.query.filter_by(name="input-output").one()
        problems = []

        hello_world = model.Problem(io_problem_type, "hello-world", "Hello, World!",
                                    'Print the string "Hello, World!"',
                                    "", "Hello, World!",
                                    "", "Hello, World!")
        problems.append(hello_world)
        test_contest.problems.append(hello_world)
        model.db.session.add(hello_world)

        hello_worlds = model.Problem(io_problem_type, "hello-worlds", "Hello, Worlds!",
                                          'Print the string "Hello, World!" n times',
                                          "3", "Hello, World!\nHello, World!\nHello, World!",
                                          "5", "Hello, World!\nHello, World!\nHello, World!\nHello, World!\nHello, World!\n")
        problems.append(hello_worlds)
        test_contest.problems.append(hello_worlds)
        model.db.session.add(hello_worlds)

        fizzbuzz = model.Problem(io_problem_type, "fizzbuzz", "FizzBuzz",
                                     "Perform fizzbuzz up to the given number\n\nMore info can be found [here](https://en.wikipedia.org/wiki/Fizz_buzz)",
                                     "3", "1\n2\nFizz",
                                     "15", "1\n2\nFizz\n4\nBuzz\nFizz\n7\n8\nFizz\nBuzz\n11\nFizz\n13\n14\nFizzBuzz\n")
        problems.append(fizzbuzz)
        test_contest.problems.append(fizzbuzz)
        model.db.session.add(fizzbuzz)

        fibonacci = model.Problem(io_problem_type, "fibonoacci", "Fibonacci",
                                  "Give the nth number in the Fibonacci sequence",
                                  "3", "2",
                                  "5", "5")
        problems.append(fibonacci)
        test_contest.problems.append(fibonacci)
        model.db.session.add(fibonacci)

        ext_fibonacci = model.Problem(io_problem_type, "ext-fib", "Extended Fibonacci",
                                      "Give the the numbers of the Fibonacci sequence between 0 and n, inclusive.\nIf n is positive, the range is [0,n].\nIf n is negative, the range is [n,0].",
                                      "-3", "2\n-1\n1\n0",
                                      "-5", "5\n-3\n2\n-1\n1\n0")
        problems.append(ext_fibonacci)
        test_contest.problems.append(ext_fibonacci)
        model.db.session.add(ext_fibonacci)

        # insert submissions
        python = model.Language.query.filter_by(name="python").one()

        solutions = {"Hello, World!": "print('Hello, World!')",
                     "Hello, Worlds!": "for i in range(int(input())):\n\tprint('Hello, World!')",
                     "FizzBuzz": 'print("\\n".join("Fizz"*(i%3==0)+"Buzz"*(i%5==0) or str(i) for i in range(1,int(input())+1)))',
                     "Fibonacci": "fib = lambda n: n if n < 2 else fib(n-1) + fib(n-2)\nprint(fib(int(input())))",
                     "Extended Fibonacci": "print('5\\n-3\\n2\\n-1\\n1\\n0')"}

        problem_subs = []
        for problem in problems:
            for user in contestants:
                for _ in range(10):
                    problem_subs.append((problem, user))

        random.shuffle(problem_subs)

        for problem, user in problem_subs:
            src_code = solutions[problem.name]
            is_submission = random.randint(1, 7) != 5

            is_priority = random.randint(1, 9) == 7
            is_correct = random.randint(1, 3) == 3
            if not is_correct:
                src_code = src_code + "\nprint('Wait this isn\\'t correct')"

            test_run = model.Run(user, test_contest, python, problem,
                                 datetime.datetime.utcnow(),
                                 src_code, problem.secret_input, problem.secret_output, is_submission)
            test_run.is_correct = is_correct
            test_run.is_priority = is_priority

            model.db.session.add(test_run)
        model.db.session.commit()


def setup_logging(app):
    """Sets up the flask app loggers"""
    formatter = logging.Formatter('%(asctime)s - %(filename)s - %(levelname)s - %(message)s')

    # remove existing handlers
    handlers = app.logger.handlers
    for handler in handlers:
        app.logger.removeHandler(handler)

    if not path.isdir(path.dirname(log_location)):
        os.makedirs(path.dirname(log_location))
    file_handler = RotatingFileHandler(log_location, maxBytes=10000, backupCount=1)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)

    stdout_handler = StreamHandler()
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.setFormatter(formatter)
    app.logger.addHandler(stdout_handler)


app = create_app()

# TODO: Moving setup functions here causes them to be executed repeatedly when nosetests is run
setup_logging(app)
setup_database(app)

if __name__ == "__main__":
    PORT = 9191
    app.logger.info("Running on port %s", PORT)
    app.run(host="0.0.0.0", port=PORT, debug=True)
