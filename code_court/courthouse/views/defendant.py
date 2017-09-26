import collections

from markdown import markdown
from enum import Enum

import util

import datetime

import model

from flask_login import current_user
from flask import (abort, Blueprint, current_app, render_template,
                   request, Markup)

defendant = Blueprint('defendant', __name__, template_folder='templates')


@defendant.route("/", methods=["GET"])
def index():
    """
    The index page for the defendant frontend

    Returns:
        a rendered defendant view template which shows all available problems
    """
    problems = model.Problem.query.all()

    return render_template("defendant/index.html", problems=problems)


RunState = Enum("RunState", "judging passed failed")

@defendant.route("/problem/<problem_id>/", methods=["GET"])
@defendant.route("/problem/<problem_id>/", methods=["POST"])
def problem(problem_id):
    problems = model.Problem.query.filter_by(id=problem_id).all()
    if len(problems) == 0:
        current_app.logger.info("Probelm %s doesn't exist", problem_id)
        abort(400)
    problem = problems[0]

    markdown_statement = Markup(markdown(problem.problem_statement))

    source_code = None
    if request.method == "POST":
        source_code = submit_code(problem)

    return render_template(
        "defendant/problem.html",
        problem=problem,
        markdown_statement=markdown_statement,
        source_code=source_code)


@defendant.route("/submissions", methods=["GET"])
def submissions():
    submissions = model.Run.query.filter_by(user=current_user, is_submission=True)\
                                 .order_by(model.Run.submit_time.desc())\
                                 .all()

    return render_template(
        "defendant/submissions.html", submissions=submissions)


def submit_code(problem):
    """
    Creates a Run object and adds it to the database

    Args:
        problem: the problem source_code is being submitted to

    Returns:
        the submitted source_code as a string
    """
    source_code = request.form.get("source_code")
    if source_code is None:
        # TODO: give better feedback for failure
        current_app.logger.info("No source code given")
        abort(400)

    current_time = datetime.datetime.utcnow()

    # Hardcoded run details for the time being
    test_user = model.User.query.filter_by(email="testuser1@example.org").one()
    test_contest = model.Contest.query.filter_by(name="test_contest").one()
    python = model.Language.query.filter_by(name="python").one()

    button_action = request.form.get("action")
    is_submission = button_action == "submit" and not button_action == "run"

    run = model.Run(test_user, test_contest, python, problem, current_time,
                    source_code, problem.secret_input, problem.secret_output,
                    is_submission)

    model.db.session.add(run)
    model.db.session.commit()

    return source_code

