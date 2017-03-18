import datetime
from time import sleep

import model
from model import db

EXECUTOR_TIMEOUT_MINS = 5

def reset_overdue_runs():
    runs = model.Run.query.filter(model.Run.finished_execing_time == None)\
               .filter(model.Run.started_execing_time != None)\
               .filter((datetime.datetime.utcnow() -
                        datetime.timedelta(minutes=EXECUTOR_TIMEOUT_MINS)) >
                        model.Run.started_execing_time).all()

    for run in runs:
        run.started_execing_time = None

    model.db.session.commit()

def event_loop():
    try:
        while True:
            reset_overdue_runs()
            sleep(30)

    except KeyboardInterrupt:
        print("Event loop shutting down")

if __name__ == "__main__":
    event_loop()
