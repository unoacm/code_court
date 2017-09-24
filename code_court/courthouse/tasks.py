import os

import uwsgidecorators

from flask import Flask

import model

@uwsgidecorators.timer(60)
def cronjob_task(signum):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        "CODE_COURT_DB_URI") or "sqlite:////tmp/code_court.db"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    model.db.init_app(app)

    with app.app_context():
        overdue_runs = model.Run.query.filter(model.Run.finished_execing_time == None)\
                   .filter(model.Run.started_execing_time != None)\
                   .filter((datetime.datetime.utcnow() -
                            datetime.timedelta(minutes=EXECUTOR_TIMEOUT_MINS)) >
                            model.Run.started_execing_time).all()

        for run in overdue_runs:
            run.started_execing_time = None

        model.db.session.commit()

