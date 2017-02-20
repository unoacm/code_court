import collections
import json
import re

from enum import Enum

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

    return render_template("defendant/defendant_index.html", problems=problems)

RunState = Enum("RunState", "judging passed failed")

@defendant.route("/scoreboard", methods=["GET"])
def scoreboard():
    model = util.get_model()

    defendants = model.User.query.filter(model.User.user_roles.any(id="defendant")).all()
    problems = model.Problem.query.all()
    contest = model.Contest.query.first() #TODO: replace with correct contest

    # compute scoreboard
    scores = collections.OrderedDict()
    for user in defendants:
        user_scores = collections.OrderedDict()
        for problem in problems:
            runs = model.Run.query.filter_by(is_submission=True, user=user, contest=contest, problem=problem).all()

            grid = []
            for run in runs:
                if not run.is_judged:
                    val = RunState.judging
                elif run.is_passed:
                    val = RunState.passed
                else:
                    val = RunState.failed
                grid.append(val)

            user_scores[problem.id] = grid
        scores[user.id] = user_scores

    return render_template("defendant/scoreboard.html", users=defendants, problems=problems, scores=scores, RunState=RunState)

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
    test_user = model.User.query.filter_by(email="testuser1@example.org").one()
    test_contest = model.Contest.query.filter_by(name="test_contest").one()
    python = model.Language.query.filter_by(name="python").one()

    button_action = request.form.get("action")
    is_submission = button_action == "submit" and not button_action == "run"

    run = model.Run(test_user, test_contest,
                    python, problem, current_time, source_code,
                    problem.secret_input, problem.secret_output, is_submission)

    model.db.session.add(run)
    model.db.session.commit()

    return source_code
