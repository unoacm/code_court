import datetime
from time import sleep

from flask import Flask

import model
from model import db

EXECUTOR_TIMEOUT_MINS = 1

def reset_overdue_runs():
    runs = model.Run.query.filter(model.Run.finished_execing_time == None)\
               .filter(model.Run.started_execing_time != None)\
               .filter((datetime.datetime.utcnow() -
                        datetime.timedelta(minutes=EXECUTOR_TIMEOUT_MINS)) >
                        model.Run.started_execing_time).all()

    for run in runs:
        print("Returning overdue run: ", run.id)
        run.started_execing_time = None

    model.db.session.commit()

def event_loop():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/code_court.db"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['model'] = model

    db.init_app(app)

    with app.app_context():
        try:
            while True:
                reset_overdue_runs()
                sleep(30)

        except KeyboardInterrupt:
            print("Event loop shutting down")

if __name__ == "__main__":
    event_loop()
