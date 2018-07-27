#!/usr/bin/env python3
"""
The entrypoint to the courthouse application
"""
import datetime
import json
import logging
import os
import random
import textwrap

from logging.handlers import RotatingFileHandler
from logging import StreamHandler
from os import path

from flask import Flask, render_template, send_from_directory, request, current_app

from flask_cors import CORS
from flask_debugtoolbar import DebugToolbarExtension
from flask_jwt_extended import JWTManager
from flask_login import LoginManager, current_user

from flask_sqlalchemy import get_debug_queries

import werkzeug

import model
import util

from database import db_session, init_db, engine

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
logging.getLogger("werkzeug").setLevel(logging.INFO)

log_location = "logs/code_court.log"

app = Flask(__name__)

CODE_COURT_PRODUCTION_ENV_VAR = "CODE_COURT_PRODUCTION"


def create_app():
    """
    Initializes the flask app object

    Returns:
        Flask: the initialized flask app
    """
    app = Flask(__name__)

    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 86400  # 1 day

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ECHO"] = False
    app.config["SQLALCHEMY_RECORD_QUERIES"] = False
    app.config["model"] = model
    app.config[
        "SECRET_KEY"
    ] = "2jrlkfjoi1j3kljekdlasjdklasjdk139999d9d"  # TODO: put this in config
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(days=30)

    if app.config.get("SSL"):
        app.config.update(dict(PREFERRED_URL_SCHEME="https"))

    app.config["RUNMODE"] = "PRODUCTION" if os.getenv(
        CODE_COURT_PRODUCTION_ENV_VAR
    ) else "DEVELOPMENT"

    # Add custom filters to Jinja2
    # http://flask.pocoo.org/docs/0.12/templating/
    app.jinja_env.filters["dt_to_str"] = util.dt_to_str
    app.jinja_env.filters["dt_to_date_str"] = util.dt_to_date_str
    app.jinja_env.filters["dt_to_time_str"] = util.dt_to_time_str

    setup_logging(app)
    app.logger.setLevel(logging.DEBUG)

    init_db()
    if not app.config["TESTING"]:
        setup_database(app)

    with app.app_context():
        app.config["MAX_CONTENT_LENGTH"] = util.get_configuration(
            "max_output_length"
        ) * 1024  # kilobytes

    CORS(app, supports_credentials=True)

    JWTManager(app)

    login_manager = LoginManager()
    login_manager.init_app(app)

    login_manager.login_view = "auth.login_view"

    DebugToolbarExtension(app)

    app.logger.info("Setting up app")

    @login_manager.user_loader
    def load_user(username):
        return model.User.query.filter_by(username=username).scalar()

    app.register_blueprint(main, url_prefix="")
    app.register_blueprint(api, url_prefix="/api")
    app.register_blueprint(admin, url_prefix="/admin")
    app.register_blueprint(configurations, url_prefix="/admin/configurations")
    app.register_blueprint(clarifications, url_prefix="/admin/clarifications")
    app.register_blueprint(languages, url_prefix="/admin/languages")
    app.register_blueprint(problems, url_prefix="/admin/problems")
    app.register_blueprint(users, url_prefix="/admin/users")
    app.register_blueprint(runs, url_prefix="/admin/runs")
    app.register_blueprint(contests, url_prefix="/admin/contests")
    app.register_blueprint(defendant, url_prefix="/defendant")
    app.register_blueprint(auth, url_prefix="/admin")

    @app.context_processor
    def inject_user():
        return {}

    @app.route("/")
    def defendant_index():
        return send_from_directory("static/defendant-frontend", "index.html")

    @app.route("/<path:path>")
    def all(path):
        try:
            return send_from_directory("static/defendant-frontend", path)
        except werkzeug.exceptions.NotFound as e:
            return send_from_directory("static/defendant-frontend", "index.html")

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(401)
    @login_manager.unauthorized_handler
    def unauthorized(callback=None):
        if not current_user.is_authenticated:
            return render_template("auth/login.html"), 401
        return render_template("401.html"), 401

    @app.teardown_appcontext
    def teardown(exception=None):
        db_session.remove()

    @app.after_request
    def after_request(resp):
        if app.config.get("SQLALCHEMY_RECORD_QUERIES"):
            with open("/home/ben/sql", "a+") as f:
                f.write("=========\n{}:\n\n".format(request.url))
                for q in get_debug_queries():
                    f.write("{}\n\n".format(q))
                f.write("=========\n\n")
        return resp

    return app


def setup_database(app):
    """Creates the database tables on initial startup"""
    with app.app_context():
        if not is_db_inited():
            populate_db()
            if not app.config["TESTING"] and app.config["RUNMODE"] == "DEVELOPMENT":
                dev_populate_db()


def is_db_inited():
    """Checks if the db is initialized

    Args:
        app: the flask app

    Returns:
        bool: True if the database has been initialized
    """
    if not engine.dialect.has_table(engine, "user_role"):
        return False
    return model.UserRole.query.count() > 0


def populate_db():
    """Performs the initial database setup for the application
    """
    current_app.logger.info("Initializing db tables")

    db_session.add_all(
        [
            model.UserRole("defendant"),
            model.UserRole("operator"),
            model.UserRole("judge"),
            model.UserRole("executioner"),
            model.UserRole("observer"),
        ]
    )

    # TODO: extract these out into a folder
    db_session.add_all(
        [
            model.Language(
                "python",
                "python",
                True,
                textwrap.dedent(
                    """
                                    #!/bin/bash
                                    cat $input_file | python3 $program_file
                                    exit $?"""
                ).strip(),
            ),
            model.Language(
                "python2",
                "python",
                True,
                textwrap.dedent(
                    """
                                    #!/bin/bash
                                    cat $input_file | python2 $program_file
                                    exit $?"""
                ).strip(),
            ),
            model.Language(
                "perl",
                "perl",
                True,
                textwrap.dedent(
                    """
                                    #!/bin/bash
                                    cat $input_file | perl $program_file
                                    exit $?"""
                ).strip(),
            ),
            model.Language(
                "lua",
                "lua",
                True,
                textwrap.dedent(
                    """
                                    #!/bin/bash
                                    cat $input_file | lua $program_file
                                    exit $?"""
                ).strip(),
            ),
            model.Language(
                "nodejs",
                "javascript",
                True,
                textwrap.dedent(
                    """
                                    #!/bin/bash
                                    cat $input_file | node $program_file
                                    exit $?"""
                ).strip(),
            ),
            model.Language(
                "guile",
                "scheme",
                True,
                textwrap.dedent(
                    """
                                    #!/bin/bash
                                    cat $input_file | guile --no-auto-compile $program_file
                                    exit $?"""
                ).strip(),
            ),
            model.Language(
                "fortran",
                "fortran",
                True,
                textwrap.dedent(
                    """
                                #!/bin/bash
                                cp /share/program $scratch_dir/program.f

                                cd $scratch_dir

                                gfortran -o program $scratch_dir/program.f

                                if [[ $? != 0 ]]; then
                                  exit $?
                                fi

                                cat $input_file | ./program

                                exit $?"""
                ).strip(),
            ),
            model.Language(
                "c",
                "clike",
                True,
                textwrap.dedent(
                    """
                                #!/bin/bash
                                cp $program_file $scratch_dir/program.c

                                cd $3

                                gcc -o program $scratch_dir/program.c

                                if [[ $? != 0 ]]; then
                                  exit $?
                                fi

                                cat $input_file | ./program

                                exit $?"""
                ).strip(),
                textwrap.dedent(
                    """
                                #include <stdio.h>

                                int main(int argc, const char* argv[]) {
                                }"""
                ),
            ),
            model.Language(
                "c++",
                "clike",
                True,
                textwrap.dedent(
                    """
                                #!/bin/bash
                                cp $program_file $scratch_dir/program.cpp

                                cd $scratch_dir

                                g++ -o program $scratch_dir/program.cpp

                                if [[ $? != 0 ]]; then
                                  exit $?
                                fi

                                cat $input_file | ./program

                                exit $?"""
                ).strip(),
                textwrap.dedent(
                    """
                                #include <iostream>

                                int main() {
                                  std::cout << "Hello World!";
                                }"""
                ),
            ),
            model.Language(
                "java",
                "clike",
                True,
                textwrap.dedent(
                    """
                                #!/bin/bash
                                export PATH=$PATH:/usr/lib/jvm/java-1.8-openjdk/bin

                                cp $program_file $scratch_dir/Main.java

                                cd $scratch_dir

                                javac Main.java

                                if [[ $? != 0 ]]; then
                                  exit $?
                                fi

                                cat $input_file | java Main

                                exit $?"""
                ).strip(),
                textwrap.dedent(
                    """
                                public class Main {
                                    public static void main(String[] args) {

                                    }
                                }"""
                ),
            ),
            model.Language(
                "ruby",
                "ruby",
                True,
                textwrap.dedent(
                    """
                                        #!/bin/bash
                                        cat $input_file | ruby $program_file
                                        exit $?"""
                ).strip(),
            ),
            model.Language(
                "rust",
                "rust",
                True,
                textwrap.dedent(
                    """
                                        #!/bin/bash
                                        cp /share/program $scratch_dir/main.rs

                                        cd $scratch_dir

                                        rustc $scratch_dir/main.rs

                                        if [[ $? != 0 ]]; then
                                          exit $?
                                        fi

                                        cat $input_file | ./main
                                        exit $?"""
                ).strip(),
                textwrap.dedent(
                    """
                                        fn main() {
                                        }
                        """
                ).strip(),
            ),
        ]
    )

    db_session.add_all(
        [
            model.Configuration("strict_whitespace_diffing", "False", "bool", "admin"),
            model.Configuration(
                "contestants_see_sample_output", "True", "bool", "defendant"
            ),
            model.Configuration("max_user_submissions", "5", "integer", "defendant"),
            model.Configuration(
                "user_submission_time_limit", "1", "integer", "defendant"
            ),
            model.Configuration(
                "max_output_length", str(10 * 1024), "integer", "defendant"
            ),
            model.Configuration(
                "run_refresh_interval_millseconds", 5000, "integer", "defendant"
            ),
            model.Configuration(
                "score_refresh_interval_millseconds", 30000, "integer", "defendant"
            ),
            model.Configuration(
                "misc_refresh_interval_millseconds", 12000, "integer", "defendant"
            ),
            model.Configuration("extra_signup_fields", "[]", "json", "defendant"),
        ]
    )

    db_session.add_all(
        [model.ProblemType("input-output", '#!/bin/bash\ntest "$1" = "$2"')]
    )
    db_session.commit()

    roles = {x.name: x for x in model.UserRole.query.all()}
    db_session.add_all(
        [
            model.User("admin", "Admin", "pass", user_roles=[roles["operator"]]),
            model.User(
                "exec", "Executioner", "epass", user_roles=[roles["executioner"]]
            ),
        ]
    )

    db_session.commit()

    # Version scraper run

    with open("init_data/printver.py", "r") as f:
        src_code = "\n".join(f.readlines())

    executioner_user = model.User.query.filter_by(username="exec").scalar()

    python = model.Language.query.filter_by(name="python").scalar()
    empty_input = ""

    version_contest = model.Contest(
        name="version_contest",
        start_time=datetime.datetime.utcnow(),
        end_time=datetime.datetime.utcnow() + datetime.timedelta(hours=1),
        is_public=True,
        activate_time=datetime.datetime.utcnow(),
        freeze_time=None,
        deactivate_time=None,
    )

    db_session.add(version_contest)
    db_session.commit()

    verscrape_run = model.Run(
        executioner_user,
        version_contest,
        python,
        None,
        datetime.datetime.utcnow(),
        src_code,
        empty_input,
        empty_input,
        True,
        None,
    )

    db_session.add(verscrape_run)

    db_session.commit()


def dev_populate_db():
    """Performs the initial database setup for the application
    """
    current_app.logger.info("Initializing tables with dev data")
    roles = {x.name: x for x in model.UserRole.query.all()}

    db_session.add_all(
        [
            model.User(
                "superuser", "SuperUser", "pass", user_roles=list(roles.values())
            ),
            model.User(
                "observer", "ObserverUser", "pass", user_roles=[roles["observer"]]
            ),
        ]
    )

    contestants = []
    names = [
        "Fred", "George", "Jenny", "Sam", "Jo", "Joe", "Sarah", "Ben", "Josiah", "Micah"
    ]
    for i in range(1, 5):
        test_contestant = model.User(
            "testuser{}".format(i),
            names[i - 1],
            "pass",
            user_roles=[roles["defendant"]],
        )
        db_session.add(test_contestant)
        contestants.append(test_contestant)

    # create test contest
    now = datetime.datetime.utcnow()
    test_contest = model.Contest(
        name="test_contest",
        start_time=now,
        end_time=now + datetime.timedelta(hours=2),
        is_public=True,
        activate_time=now,
        freeze_time=None,
        deactivate_time=None,
    )
    test_contest.users += contestants
    db_session.add(test_contest)

    io_problem_type = model.ProblemType.query.filter_by(name="input-output").one()
    problems = []

    hello_world = model.Problem(
        io_problem_type,
        "hello-world",
        "Hello, World!",
        'Print the string "Hello, World!"',
        "",
        "Hello, World!",
        "",
        "Hello, World!",
    )
    problems.append(hello_world)
    test_contest.problems.append(hello_world)
    db_session.add(hello_world)

    n = 5000
    hello_worlds = model.Problem(
        io_problem_type,
        "hello-worlds",
        "Hello, Worlds!",
        'Print the string "Hello, World!" n times',
        "2",
        "Hello, World!\nHello, World!",
        str(n),
        "Hello, World!\n" * n,
    )
    problems.append(hello_worlds)
    test_contest.problems.append(hello_worlds)
    db_session.add(hello_worlds)

    fizzbuzz = model.Problem(
        io_problem_type,
        "fizzbuzz",
        "FizzBuzz",
        "Perform fizzbuzz up to the given number\n\nMore info can be found [here](https://en.wikipedia.org/wiki/Fizz_buzz)",
        "3",
        "1\n2\nFizz",
        "15",
        "1\n2\nFizz\n4\nBuzz\nFizz\n7\n8\nFizz\nBuzz\n11\nFizz\n13\n14\nFizzBuzz\n",
    )
    problems.append(fizzbuzz)
    test_contest.problems.append(fizzbuzz)
    db_session.add(fizzbuzz)

    fibonacci = model.Problem(
        io_problem_type,
        "fibonoacci",
        "Fibonacci",
        "Give the nth number in the Fibonacci sequence",
        "4",
        "3",
        "5",
        "5",
    )
    problems.append(fibonacci)
    test_contest.problems.append(fibonacci)
    db_session.add(fibonacci)

    ext_fibonacci = model.Problem(
        io_problem_type,
        "ext-fib",
        "Extended Fibonacci",
        "Give the the numbers of the Fibonacci sequence between 0 and n, inclusive.\nIf n is positive, the range is [0,n].\nIf n is negative, the range is [n,0].",
        "-3",
        "2\n-1\n1\n0",
        "-5",
        "5\n-3\n2\n-1\n1\n0",
    )
    problems.append(ext_fibonacci)
    test_contest.problems.append(ext_fibonacci)
    db_session.add(ext_fibonacci)

    # insert submissions
    python = model.Language.query.filter_by(name="python").one()

    solutions = {
        "Hello, World!": "print('Hello, World!')",
        "Hello, Worlds!": "for i in range(int(input())):\n\tprint('Hello, World!')",
        "FizzBuzz": 'print("\\n".join("Fizz"*(i%3==0)+"Buzz"*(i%5==0) or str(i) for i in range(1,int(input())+1)))',
        "Fibonacci": "fib = lambda n: n if n < 2 else fib(n-1) + fib(n-2)\nprint(fib(int(input())))",
        "Extended Fibonacci": "print('5\\n-3\\n2\\n-1\\n1\\n0')",
    }

    problem_subs = []
    for problem in problems:
        for user in contestants:
            for _ in range(2):
                problem_subs.append((problem, user))

    random.shuffle(problem_subs)

    for problem, user in problem_subs:
        src_code = solutions[problem.name]
        is_submission = random.randint(1, 7) != 5

        is_priority = random.randint(1, 9) == 7
        is_correct = random.randint(1, 2) == 2
        if not is_correct:
            src_code = src_code + "\nprint('Wait this isn\\'t correct')"

        test_run = model.Run(
            user,
            test_contest,
            python,
            problem,
            datetime.datetime.utcnow(),
            src_code,
            problem.secret_input,
            problem.secret_output,
            is_submission,
        )
        test_run.is_correct = is_correct
        test_run.is_priority = is_priority
        test_run.state = model.RunState.JUDGING

        db_session.add(test_run)

    util.set_configuration("extra_signup_fields", json.dumps(["email"]))

    db_session.commit()


def setup_logging(app):
    """Sets up the flask app loggers"""
    formatter = logging.Formatter(
        "%(asctime)s - %(filename)s - %(levelname)s - %(message)s"
    )

    # remove existing handlers
    handlers = app.logger.handlers
    for handler in handlers:
        app.logger.removeHandler(handler)

    if not path.isdir(path.dirname(log_location)):
        os.makedirs(path.dirname(log_location))
    file_handler = RotatingFileHandler(log_location, maxBytes=10000, backupCount=2)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)

    stdout_handler = StreamHandler()
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.setFormatter(formatter)
    app.logger.addHandler(stdout_handler)


app = create_app()

if __name__ == "__main__":
    PORT = 9191
    app.logger.info("Running on port %s", PORT)
    app.run(host="0.0.0.0", port=PORT, debug=True)
