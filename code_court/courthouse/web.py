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

import models

from models import db

from views.admin import admin
from views.api import api
from views.main import main

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

    db.init_app(app)

    app.logger.setLevel(logging.INFO)

    app.register_blueprint(main, url_prefix='')
    app.register_blueprint(admin, url_prefix='/admin')

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
        app.logger.info("Creating db tables")
        db.create_all()

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

    setup_database(app)
    setup_logging(app)

    app.logger.info("Running on port %s", PORT)
    app.run(host="0.0.0.0", port=PORT, debug=True)
