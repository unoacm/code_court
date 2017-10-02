import util


from flask import (
    Blueprint,
    current_app,
    redirect,
    render_template,
    request,
    url_for, )

import model
from database import db_session

runs = Blueprint('runs', __name__, template_folder='templates/runs')


class ModelMissingException(Exception):
    pass


@runs.route("/", methods=["GET"], defaults={'page': 1})
@runs.route("/<int:page>/", methods=["GET"])
@util.login_required("operator")
def runs_view(page):
    """
    The runs view page

    Returns:
        a rendered runs view template
    """
    run_type = request.args.get("run_type")
    run_status = request.args.get("run_status")

    num_pending = model.Run.query.filter_by(finished_execing_time=None).count()

    if run_type == "submissions":
        run_query = model.Run.query.filter_by(is_submission=True)
    elif run_type == "tests":
        run_query = model.Run.query.filter_by(is_submission=False)
    else:
        run_query = model.Run.query

    if run_status == "judged":
        run_query = run_query.filter(model.Run.finished_execing_time is not None)
    elif run_status == "pending":
        run_query = run_query.filter_by(finished_execing_time=None)

    runs = util.paginate(run_query.order_by(model.Run.submit_time.desc()), page, 30)

    return render_template(
        "runs/view.html",
        runs=runs,
        run_type=run_type,
        run_status=run_status,
        num_pending=num_pending)


@runs.route("/run/<int:run_id>/", methods=["GET"])
@util.login_required("operator")
def runs_run(run_id):
    """
    Displays the run page

    Params:
        run_id (int): the run to view

    Returns:
        a rendered view run template
    """
    run = model.Run.query.filter_by(id=run_id).scalar()

    return render_template("runs/run.html", run=run)


@runs.route("/<int:run_id>/priority", methods=["GET"])
def priority(run_id):
    run = model.Run.query.get(run_id)
    run.is_priority = not run.is_priority

    db_session.add(run)
    db_session.commit()

    return redirect(url_for("runs.runs_run", run_id=run_id))

@runs.route("/<int:run_id>/rejudge", methods=["GET"])
def rejudge(run_id):
    run = model.Run.query.get(run_id)

    run.started_execing_time = None
    run.finished_execing_time = None
    run.run_output = None
    if run.is_submission:
        run.run_input = run.problem.secret_input
        run.correct_output = run.problem.secret_output

    db_session.commit()

    return redirect(url_for("runs.runs_run", run_id=run_id))
