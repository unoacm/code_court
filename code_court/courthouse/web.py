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

from flask import Flask, render_template, send_from_directory

from flask_cors import CORS
from flask_debugtoolbar import DebugToolbarExtension
from flask_jwt_extended import JWTManager
from flask_login import LoginManager, current_user

import werkzeug

import model
import util

from model import db

from views.main import main
from views.api import api
from views.admin.admin import admin
from views.admin.configurations import configurations
from views.admin.clarifications import clarifications
from views.admin.languages import languages
from views.admin.problems import problems
from views.admin.users import users
from views.admin.runs import runs
from views.admin.contests import contests
from views.defendant import defendant
from views.auth import auth


# turn down log level for werkzeug
wlog = logging.getLogger('werkzeug')
wlog.setLevel(logging.INFO)

log_location = 'logs/code_court.log'

app = Flask(__name__)

CODE_COURT_PRODUCTION_ENV_VAR = "CODE_COURT_PRODUCTION"


def create_app():
    """
    Initializes the flask app object

    Returns:
        Flask: the initialized flask app
    """
    app = Flask(__name__)


    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 86400  # 1 day

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        "CODE_COURT_DB_URI") or "sqlite:////tmp/code_court.db"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = False
    app.config['model'] = model
    app.config[
        'SECRET_KEY'] = '2jrlkfjoi1j3kljekdlasjdklasjdk139999d9d'  #TODO: put this in config
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=30)

    if app.config.get("SSL"):
        app.config.update(dict(PREFERRED_URL_SCHEME='https'))

    app.config['RUNMODE'] = "PRODUCTION" if os.getenv(CODE_COURT_PRODUCTION_ENV_VAR) else "DEVELOPMENT"

    # Add datetime to string filter to Jinja2
    # http://flask.pocoo.org/docs/0.12/templating/
    app.jinja_env.filters['dt_to_str'] = model.dt_to_str
    app.jinja_env.filters['dt_to_date_str'] = model.dt_to_date_str
    app.jinja_env.filters['dt_to_time_str'] = model.dt_to_time_str

    db.init_app(app)
    if not app.config['TESTING']:
        setup_database(app)

    with app.app_context():
        app.config['MAX_CONTENT_LENGTH'] = util.get_configuration(
            "max_output_length") * 1024  # kilobytes

    CORS(app)

    JWTManager(app)

    login_manager = LoginManager()
    login_manager.init_app(app)

    login_manager.login_view = "auth.login_view"

    DebugToolbarExtension(app)

    @login_manager.user_loader
    def load_user(user_email):
        return model.User.query.filter_by(email=user_email).one()

    app.logger.setLevel(logging.DEBUG)

    app.register_blueprint(main, url_prefix='')
    app.register_blueprint(api, url_prefix='/api')
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(configurations, url_prefix='/admin/configurations')
    app.register_blueprint(clarifications, url_prefix='/admin/clarifications')
    app.register_blueprint(languages, url_prefix='/admin/languages')
    app.register_blueprint(problems, url_prefix='/admin/problems')
    app.register_blueprint(users, url_prefix='/admin/users')
    app.register_blueprint(runs, url_prefix='/admin/runs')
    app.register_blueprint(contests, url_prefix='/admin/contests')
    app.register_blueprint(defendant, url_prefix='/defendant')
    app.register_blueprint(auth, url_prefix='/admin')

    @app.context_processor
    def inject_user():
        return {}

    @app.route('/')
    def defendant_index():
        return send_from_directory('static/defendant-frontend', "index.html")

    @app.route('/<path:path>')
    def all(path):
        try:
            return send_from_directory('static/defendant-frontend', path)
        except werkzeug.exceptions.NotFound as e:
            return send_from_directory('static/defendant-frontend',
                                       "index.html")

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
            if not app.config['TESTING'] and app.config['RUNMODE'] == "DEVELOPMENT":
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

        model.db.session.add_all([
            model.UserRole("defendant"),
            model.UserRole("operator"),
            model.UserRole("judge"),
            model.UserRole("executioner"),
            model.UserRole("observer")
        ])

        # TODO: extract these out into a folder
        model.db.session.add_all([
            model.Language("python", "python", True,
                           textwrap.dedent('''
                                        #!/bin/bash
                                        cat $1 | python3 $2
                                        exit $?''').strip()),
            model.Language("python2", "python", True,
                           textwrap.dedent('''
                                        #!/bin/bash
                                        cat $1 | python2 $2
                                        exit $?''').strip()),
            model.Language("perl", "perl", True,
                           textwrap.dedent('''
                                        #!/bin/bash
                                        cat $1 | perl $2
                                        exit $?''').strip()),
            model.Language("lua", "lua", True,
                           textwrap.dedent('''
                                        #!/bin/bash
                                        cat $1 | lua $2
                                        exit $?''').strip()),
            model.Language("nodejs", "javascript", True,
                           textwrap.dedent('''
                                        #!/bin/bash
                                        cat $1 | node $2
                                        exit $?''').strip()),
            model.Language("guile", "scheme", True,
                           textwrap.dedent('''
                                        #!/bin/bash
                                        cat $1 | guile --no-auto-compile $2
                                        exit $?''').strip()),
            model.Language("fortran", "fortran", True,
                           textwrap.dedent('''
                                    #!/bin/bash
                                    cp /share/program /scratch/program.f

                                    cd /scratch

                                    gfortran -o program /scratch/program.f

                                    if [[ $? != 0 ]]; then
                                      exit $?
                                    fi

                                    cat $1 | ./program

                                    exit $?''').strip()),
            model.Language("c", "clike", True,
                           textwrap.dedent('''
                                    #!/bin/bash
                                    cp /share/program /scratch/program.c

                                    cd /scratch

                                    gcc -o program /scratch/program.c

                                    if [[ $? != 0 ]]; then
                                      exit $?
                                    fi

                                    cat $1 | ./program

                                    exit $?''').strip(),
                           textwrap.dedent('''
                                    #include <stdio.h>

                                    int main(int argc, const char* argv[]) {
                                    }''')),
            model.Language("c++", "clike", True,
                           textwrap.dedent('''
                                    #!/bin/bash
                                    cp /share/program /scratch/program.cpp

                                    cd /scratch

                                    g++ -o program /scratch/program.cpp

                                    if [[ $? != 0 ]]; then
                                      exit $?
                                    fi

                                    cat $1 | ./program

                                    exit $?''').strip(),
                           textwrap.dedent('''
                                    #include <iostream>

                                    int main() {
                                      std::cout << "Hello World!";
                                    }''')),
            model.Language("java", "clike", True,
                           textwrap.dedent('''
                                    #!/bin/bash
                                    cp /share/program /scratch/Main.java

                                    cd /scratch

                                    /usr/lib/jvm/java-1.8-openjdk/bin/javac Main.java

                                    if [[ $? != 0 ]]; then
                                      exit $?
                                    fi

                                    cat $1 | /usr/lib/jvm/java-1.8-openjdk/bin/java Main

                                    exit $?''').strip(),
                           textwrap.dedent('''
                                    public class Main {
                                        public static void main(String[] args) {

                                        }
                                    }''')),
            model.Language("ruby", "ruby", True,
                           textwrap.dedent('''
                                            #!/bin/bash
                                            cat $1 | ruby $2
                                            exit $?''').strip())
        ])

        model.db.session.add_all([
            model.Configuration("strict_whitespace_diffing", "False", "bool",
                                "admin"),
            model.Configuration("contestants_see_sample_output", "True",
                                "bool", "defendant"),
            model.Configuration("max_user_submissions", "5", "integer",
                                "defendant"),
            model.Configuration("user_submission_time_limit", "1", "integer",
                                "defendant"),
            model.Configuration("max_output_length",
                                str(10 * 1024), "integer", "defendant")
        ])

        model.db.session.add_all([
            model.ProblemType("input-output", '#!/bin/bash\ntest "$1" = "$2"')
        ])

        roles = {x.name: x for x in model.UserRole.query.all()}
        model.db.session.add_all([
            model.User(
                "admin@example.org",
                "Admin",
                "pass",
                user_roles=[roles['operator']]),
            model.User(
                "exec@example.org",
                "Executioner",
                "epass",
                user_roles=[roles['executioner']])
        ])

        model.db.session.commit()


def dev_init_db(app):
    """Performs the initial database setup for the application
    """
    with app.app_context():
        app.logger.info("Initializing tables with dev data")
        roles = {x.name: x for x in model.UserRole.query.all()}

        model.db.session.add_all([
            model.User(
                "super@example.org",
                "SuperUser",
                "pass",
                user_roles=list(roles.values())),
            model.User(
                "observer@example.org",
                "ObserverUser",
                "pass",
                user_roles=[roles['observer']])
        ])

        contestants = []
        names = [
            "Fred", "George", "Jenny", "Sam", "Jo", "Joe", "Sarah", "Ben",
            "Josiah", "Micah"
        ]
        for i in range(1, 11):
            test_contestant = model.User(
                "testuser{}@example.org".format(i),
                names[i - 1],
                "pass",
                user_roles=[roles['defendant']])
            model.db.session.add(test_contestant)
            contestants.append(test_contestant)

        # create test contest
        now = datetime.datetime.utcnow()
        test_contest = model.Contest(
            name="test_contest",
            start_time=now,
            end_time=now + datetime.timedelta(minutes=30),
            is_public=True,
            activate_time=now,
            freeze_time=None,
            deactivate_time=None)
        test_contest.users += contestants
        model.db.session.add(test_contest)

        io_problem_type = model.ProblemType.query.filter_by(
            name="input-output").one()
        problems = []

        hello_world = model.Problem(io_problem_type, "hello-world",
                                    "Hello, World!",
                                    'Print the string "Hello, World!"', "",
                                    "Hello, World!", "", "Hello, World!")
        problems.append(hello_world)
        test_contest.problems.append(hello_world)
        model.db.session.add(hello_world)

        hello_worlds = model.Problem(
            io_problem_type, "hello-worlds", "Hello, Worlds!",
            'Print the string "Hello, World!" n times', "2",
            "Hello, World!\nHello, World!", "5",
            "Hello, World!\nHello, World!\nHello, World!\nHello, World!\nHello, World!\n"
        )
        problems.append(hello_worlds)
        test_contest.problems.append(hello_worlds)
        model.db.session.add(hello_worlds)

        fizzbuzz = model.Problem(
            io_problem_type, "fizzbuzz", "FizzBuzz",
            "Perform fizzbuzz up to the given number\n\nMore info can be found [here](https://en.wikipedia.org/wiki/Fizz_buzz)",
            "3", "1\n2\nFizz", "15",
            "1\n2\nFizz\n4\nBuzz\nFizz\n7\n8\nFizz\nBuzz\n11\nFizz\n13\n14\nFizzBuzz\n"
        )
        problems.append(fizzbuzz)
        test_contest.problems.append(fizzbuzz)
        model.db.session.add(fizzbuzz)

        fibonacci = model.Problem(
            io_problem_type, "fibonoacci", "Fibonacci",
            "Give the nth number in the Fibonacci sequence", "4", "3", "5",
            "5")
        problems.append(fibonacci)
        test_contest.problems.append(fibonacci)
        model.db.session.add(fibonacci)

        ext_fibonacci = model.Problem(
            io_problem_type, "ext-fib", "Extended Fibonacci",
            "Give the the numbers of the Fibonacci sequence between 0 and n, inclusive.\nIf n is positive, the range is [0,n].\nIf n is negative, the range is [n,0].",
            "-3", "2\n-1\n1\n0", "-5", "5\n-3\n2\n-1\n1\n0")
        problems.append(ext_fibonacci)
        test_contest.problems.append(ext_fibonacci)
        model.db.session.add(ext_fibonacci)

        # insert submissions
        python = model.Language.query.filter_by(name="python").one()

        solutions = {
            "Hello, World!":
            "print('Hello, World!')",
            "Hello, Worlds!":
            "for i in range(int(input())):\n\tprint('Hello, World!')",
            "FizzBuzz":
            'print("\\n".join("Fizz"*(i%3==0)+"Buzz"*(i%5==0) or str(i) for i in range(1,int(input())+1)))',
            "Fibonacci":
            "fib = lambda n: n if n < 2 else fib(n-1) + fib(n-2)\nprint(fib(int(input())))",
            "Extended Fibonacci":
            "print('5\\n-3\\n2\\n-1\\n1\\n0')"
        }

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
            is_correct = random.randint(1, 2) == 2
            if not is_correct:
                src_code = src_code + "\nprint('Wait this isn\\'t correct')"

            test_run = model.Run(user, test_contest, python, problem,
                                 datetime.datetime.utcnow(), src_code,
                                 problem.secret_input, problem.secret_output,
                                 is_submission)
            test_run.is_correct = is_correct
            test_run.is_priority = is_priority
            test_run.state = "Judging"

            model.db.session.add(test_run)
        model.db.session.commit()


def setup_logging(app):
    """Sets up the flask app loggers"""
    formatter = logging.Formatter(
        '%(asctime)s - %(filename)s - %(levelname)s - %(message)s')

    # remove existing handlers
    handlers = app.logger.handlers
    for handler in handlers:
        app.logger.removeHandler(handler)

    if not path.isdir(path.dirname(log_location)):
        os.makedirs(path.dirname(log_location))
    file_handler = RotatingFileHandler(
        log_location, maxBytes=10000, backupCount=1)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)

    stdout_handler = StreamHandler()
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.setFormatter(formatter)
    app.logger.addHandler(stdout_handler)


app = create_app()

import sys
# from werkzeug.contrib.profiler import ProfilerMiddleware
# app.wsgi_app = ProfilerMiddleware(app.wsgi_app)

setup_logging(app)

if __name__ == "__main__":
    PORT = 9191
    app.logger.info("Running on port %s", PORT)
    app.run(host="0.0.0.0", port=PORT, debug=True)
