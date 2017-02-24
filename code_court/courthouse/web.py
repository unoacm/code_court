#!/usr/bin/env python3
"""
The entrypoint to the courthouse application
"""
import logging
import os
import random

from logging.handlers import RotatingFileHandler
from logging import StreamHandler
from os import path

from flask import Flask, render_template

from flask_login import LoginManager, current_user
from flask_debugtoolbar import DebugToolbarExtension

import model

from model import db

from views.main import main
from views.api import api
from views.admin.admin import admin
from views.admin.languages import languages
from views.admin.problems import problems
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
    # app.debug = True

    # Add datetime to string filter to Jinja2
    # http://flask.pocoo.org/docs/0.12/templating/
    app.jinja_env.filters['dt_to_str'] = model.dt_to_str

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)

    login_manager.login_view = "auth.login_view"

    toolbar = DebugToolbarExtension(app)

    @login_manager.user_loader
    def load_user(user_email):
        return model.User.query.filter_by(email=user_email).one()

    app.logger.setLevel(logging.INFO)

    app.register_blueprint(main, url_prefix='')
    app.register_blueprint(api, url_prefix='/api')
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(languages, url_prefix='/admin/languages')
    app.register_blueprint(problems, url_prefix='/admin/problems')
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

        model.db.session.add_all([model.Language("python", True, '#!/bin/bash\ncat $1 | python $2\nexit $?')])

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
        for problem_num in range(1,5):
            test_problem = model.Problem(io_problem_type, "fizzbuzz{}".format(problem_num),
                                         "Perform fizzbuzz up to the given number".format(problem_num),
                                         "3", "1\n2\nFizz",
                                         "15", "1\n2\nFizz\n4\nBuzz\nFizz\n7\n8\nFizz\nBuzz\n11\nFizz\n13\n14\nFizzBuzz\n")
            problems.append(test_problem)
            test_contest.problems.append(test_problem)
            model.db.session.add(test_problem)

        # insert submissions
        python = model.Language.query.filter_by(name="python").one()
        for user in contestants:
            for problem in problems:
                for i in range(10):
                    src_code = 'print("\\n".join("Fizz"*(i%3==0)+"Buzz"*(i%5==0) or str(i) for i in range(1,int(input())+1)))'
                    is_submission = random.randint(1, 7) != 5

                    is_correct = random.randint(1, 3) == 3
                    if not is_correct:
                        src_code = src_code.replace("3", "4")

                    test_run = model.Run(user, test_contest, python, problem,
                                         model.str_to_dt("2017-02-05T23:{}".format(i)),
                                         src_code, test_problem.secret_input, test_problem.secret_output, is_submission)
                    test_run.is_correct = is_correct

                    if is_correct and is_submission:
                        break
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
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)

    stdout_handler = StreamHandler()
    stdout_handler.setLevel(logging.INFO)
    stdout_handler.setFormatter(formatter)
    app.logger.addHandler(stdout_handler)


app = create_app()
if __name__ == "__main__":
    PORT = 9191

    setup_logging(app)
    setup_database(app)

    app.logger.info("Running on port %s", PORT)
    app.run(host="0.0.0.0", port=PORT, debug=True)
