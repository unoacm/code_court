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

    run_type = request.form.get("run_type")
    run_status = request.form.get("run_status")

    num_pending = model.Run.query.filter_by(finished_execing_time=None).count()

    if run_type == "submissions":
        run_query = model.Run.query.filter_by(is_submission=True)
    elif run_type == "tests":
        run_query = model.Run.query.filter_by(is_submission=False)
    else:
        run_query = model.Run.query

    if run_status == "judged":
        run_query = run_query.filter(model.Run.finished_execing_time != None)
    elif run_status == "pending":
        run_query = run_query.filter_by(finished_execing_time=None)

    runs = run_query.order_by(model.Run.submit_time.desc()).all()

    return render_template("runs/view.html", runs=runs, 
                                             run_type=run_type, 
                                             run_status=run_status, 
                                             num_pending=num_pending)


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
