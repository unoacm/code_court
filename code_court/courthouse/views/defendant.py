import json
import re

import util

import datetime

from flask import (
    abort,
    Blueprint,
    current_app,
    render_template,
    redirect,
    request,
    url_for,
)

defendant = Blueprint('defendant', __name__,
                  template_folder='templates')

@defendant.route("/", methods=["GET"])
def index():
    """
    The index page for the defendant frontend

    Returns:
        a rendered defendant view template which shows all available problems
    """

    model = util.get_model()

    problems = model.Problem.query.all()

    return render_template("defendant_index.html", problems=problems)

@defendant.route("/problem/<problem_id>/", methods=["GET"])
@defendant.route("/problem/<problem_id>/", methods=["POST"])
def problem(problem_id):

    model = util.get_model()

    problems = model.Problem.query.filter_by(id=problem_id).all()
    if len(problems) == 0:
        current_app.logger.info("Probelm %s doesn't exist", problem_id)
        abort(400)
    problem = problems[0]

    source_code = None
    if request.method == "POST":
        source_code = submit_code(problem)

    return render_template("defendant_problem.html", problem=problem,
                            source_code=source_code)

def submit_code(problem):
    """
    Creates a Run object and adds it to the database

    Args:
        problem: the problem source_code is being submitted to

    Returns:
        the submitted source_code as a string
    """

    model = util.get_model()

    source_code = request.form.get("source_code")
    if source_code is None:
        # TODO: give better feedback for failure
        current_app.logger.info("No source code given")
        abort(400)

    current_time = datetime.datetime.utcnow()

    # Hardcoded run details for the time being
    test_user = model.User.query.filter_by(email="testuser@example.com").one()
    test_contest = model.Contest.query.filter_by(name="test_contest").one()
    python = model.Language.query.filter_by(name="python").one()

    run = model.Run(test_user, test_contest,
                    python, problem, current_time, source_code,
                    problem.secret_input, problem.secret_output, True)

    model.db.session.add(run)
    model.db.session.commit()

    return source_code
