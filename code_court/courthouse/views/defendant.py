import collections
import json
import re

from enum import Enum

import util

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

@defendant.route("/", methods=["GET", "POST"], defaults={'lang_id': None})
@defendant.route("/<int:lang_id>/", methods=["GET"])
def index(lang_id):
    """
    The index page for the defendant frontend
    """
    model = util.get_model()

    languages = model.Language.query.all()

    selected_language = model.Language.query.filter_by(id=lang_id).all()
    if len(selected_language) == 0:
        current_app.logger.info("Language %s doesn't exist", lang_id)
        abort(400)

    selection = selected_language[0].name
    return render_template("defendant/defendant_index.html", languages=languages, selection=selection)

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
