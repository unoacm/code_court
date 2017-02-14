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
#@defendant.route("/<int:lang_id>/", methods=["GET"])
def index():
    """
    The index page for the defendant frontend

    Returns:
        a rendered defendant view template which shows all available problems
    """

    model = get_model()

    problems = model.Problem.query.all()

    return render_template("defendant_index.html", problems=problems)

@defendant.route("/problem/<problem_id>/", methods=["GET"])
@defendant.route("/problem/<problem_id>/", methods=["POST"])
def problem(problem_id):

    model = get_model()

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
    
    model = get_model()

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

    #def __init__(self, user, contest, language, problem, submit_time, source_code, run_input, is_submission):
    run = model.Run(test_user, test_contest, python, problem, current_time, source_code, problem.secret_input, True)

    model.db.session.add(run)
    model.db.session.commit()

    return source_code

## Util functions
def get_model():
    """
    Gets the model from the current app,

    Note:
        must be called from within a request context

    Raises:
        ModelMissingException: if the model is not accessible from the current_app

    Returns:
        the model module
    """
    model = current_app.config.get('model')
    if model is None:
        raise ModelMissingException()
    return model
