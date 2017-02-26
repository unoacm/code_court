import json
import re
import sqlalchemy

import util

from flask_login import login_required

from flask import (
    abort,
    Blueprint,
    current_app,
    render_template,
    redirect,
    request,
    url_for,
)

runs = Blueprint('runs', __name__,
                  template_folder='templates/runs')

class ModelMissingException(Exception):
    pass

@runs.route("/", methods=["GET", "POST"])
@util.login_required("operator")
def runs_view():
    """
    The runs view page

    Returns:
        a rendered runs view template
    """
    model = util.get_model()

    runs_filter = request.form.get("filter")

    if runs_filter == "submissions":
        runs = model.Run.query.filter_by(is_submission=True).all()
    elif runs_filter == "judged":
        runs = []
        query = model.Run.query.filter_by(is_submission=True).all()
        for run in query:
            if run.is_judged:
                runs.append(run)
    elif runs_filter == "not_judged":
        runs = model.Run.query.filter_by(is_submission=True, finished_execing_time=None).all()
    elif runs_filter == "tests":
        runs = model.Run.query.filter_by(is_submission=False).all()
    else:
        runs = model.Run.query.all()

    return render_template("runs/view.html", runs=runs, runs_filter=runs_filter)


@runs.route("/<int:run_id>/", methods=["GET"])
@util.login_required("operator")
def runs_run(run_id):
    """
    Displays the run page

    Params:
        run_id (int): the run to view

    Returns:
        a rendered view run template
    """
    model = util.get_model()

    run = model.Run.query.filter_by(id=run_id).one()

    return render_template("runs/run.html", run=run)
