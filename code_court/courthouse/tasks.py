"""
Defines tasks for uwsgi to run at regular intervals
"""
import datetime
import os

import uwsgidecorators

from flask import Flask

import model
from database import db_session

EXECUTOR_TIMEOUT_MINS = 3


@uwsgidecorators.timer(15, target="spooler")
def reset_overdue_runs(signum):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        "CODE_COURT_DB_URI") or "sqlite:////tmp/code_court.db"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # reset overdue runs
    overdue_runs = model.Run.query.filter(model.Run.finished_execing_time == None)\
               .filter(model.Run.started_execing_time != None)\
               .filter((datetime.datetime.utcnow() -
                        datetime.timedelta(minutes=EXECUTOR_TIMEOUT_MINS)) >
                        model.Run.started_execing_time).all()

    for run in overdue_runs:
        run.started_execing_time = None

    db_session.commit()
