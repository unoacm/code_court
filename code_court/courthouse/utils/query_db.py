#!/usr/bin/env python

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import datetime

import IPython

from flask import Flask

import model
from database import db_session

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "CODE_COURT_DB_URI"
) or "sqlite:////tmp/code_court.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["model"] = model


def _main():
    with app.app_context():
        IPython.embed()


def submit_fake_run(username):
    lang = model.Language.query.filter_by(name="python").scalar()
    problem = model.Problem.query.first()
    contest = model.Contest.query.first()
    user = model.User.query.filter_by(username=username).scalar()

    run_input = problem.secret_input
    run_output = problem.secret_output
    is_submission = True
    source_code = 'print("Hello")'

    run = model.Run(
        user,
        contest,
        lang,
        problem,
        datetime.datetime.utcnow(),
        source_code,
        run_input,
        run_output,
        is_submission,
    )

    model.db.session.add(run)
    model.db.session.commit()


if __name__ == "__main__":
    _main()
