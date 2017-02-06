#!/usr/bin/env python3
"""
The entrypoint to the courthouse application
"""
import logging
import os

from logging.handlers import RotatingFileHandler
from logging import StreamHandler
from os import path

from flask import Flask, render_template

import model

from model import db

from views.main import main
from views.api import api
from views.admin.admin import admin
from views.admin.languages import languages
from views.defendant import defendant

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

    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/code_court.db"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['model'] = model

    db.init_app(app)

    app.logger.setLevel(logging.INFO)

    app.register_blueprint(main, url_prefix='')
    app.register_blueprint(api, url_prefix='/api')
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(languages, url_prefix='/admin/languages')
    app.register_blueprint(defendant, url_prefix='/defendant')

    @app.context_processor
    def inject_user():
        return {
        }

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    return app

def setup_database(app):
    """Creates the database tables on initial startup"""
    with app.app_context():
        if not is_db_inited(app):
            app.logger.info("Creating db tables")
            db.create_all()
            db.session.commit()
            init_db(app)

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
                                 model.UserRole("judge")])

        model.db.session.add_all([model.Language("python", True, "#!/bin/bash\npython $1")])

        model.db.session.add_all([model.Configuration("strict_whitespace_diffing", "False", "bool"),
                                  model.Configuration("contestants_see_sample_output", "True", "bool")])
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
