import json
import re
import datetime
import util

import uuid

from sqlalchemy.exc import IntegrityError

from flask_login import login_required
from flask_login import current_user


from flask import (
    abort,
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
    flash,
)

import model
from database import db_session

clarifications = Blueprint(
    "clarifications", __name__, template_folder="templates/clarifications"
)


class ModelMissingException(Exception):
    pass


@clarifications.route("/", methods=["GET"])
@util.login_required("operator")
def clarifications_view():
    """
    The clarifications view page

    Returns:
        a rendered clarifications view template
    """
    clarifications = model.Clarification.query.all()

    return render_template("clarifications/view.html", clarifications=clarifications)


@clarifications.route("/add/", methods=["GET", "POST"])
@util.login_required("operator")
def clarifications_add():
    """
    Displays the clarification adding and accepts form submits from those pages.

    Returns:
        a rendered add/edit template or a redirect to the clarification view page
    """
    if request.method == "GET":  # display add form
        problems = [x.name for x in model.Problem.query.all()]
        return render_template(
            "clarifications/add.html", action_label="Add", problems=problems
        )
    elif request.method == "POST":  # add the clarification to db
        return add_clar()
    else:
        current_app.logger.info("invalid clar add request method: %s", request.method)
        abort(400)


@clarifications.route("/del/<clar_id>/", methods=["GET"])
@util.login_required("operator")
def clarifications_del(clar_id):
    """
    Deletes a clarification

    Params:
        clar_id (int): the clarification to delete

    Returns:
        a redirect to the clarification view page
    """
    clar = model.Clarification.query.filter_by(id=clar_id).scalar()
    if clar is None:
        error = "Failed to delete clarification '{}' as it doesn't exist.".format(
            clar_id
        )
        current_app.logger.info(error)
        flash(error, "danger")
        return redirect(url_for("clarifications.clarifications_view"))

    try:
        db_session.delete(clar)
        db_session.commit()
        flash("Deleted clarification '{}'".format(clar_id), "warning")
    except IntegrityError:
        db_session.rollback()
        error = "Failed to delete clarification '{}' as it's referenced in another DB element".format(
            clar_id
        )
        current_app.logger.info(error)
        flash(error, "danger")

    return redirect(url_for("clarifications.clarifications_view"))


@clarifications.route("/answer/<clar_id>", methods=["GET", "POST"])
@util.login_required("operator")
def clarifications_answer(clar_id):
    """
    Answers a clarification"

    Returns:
        a redirect to the clarification view page
    """
    if request.method == "GET":  # Just going to the page to answer it
        clarification = model.Clarification.query.filter_by(id=clar_id).first()
        return render_template(
            "clarifications/answer.html",
            action_label="Answer",
            clarification=clarification,
        )
    elif request.method == "POST":  # answer submitted
        return answer_clar()
    else:
        current_app.logger.info(
            "invalid clar answer request method: %s", request.method
        )
        abort(400)


def add_clar():
    """
    Adds a clarification

    Note:
        must be called from within a request context

    Returns:
        a redirect to the clarification view page
    """

    problem_input = request.form.get("problem")
    subject = request.form.get("subject")
    contents = request.form.get("contents")

    if subject is None:
        error = "Failed to add clarification due to undefined subject."
        current_app.logger.info(error)
        flash(error, "danger")
        return redirect(url_for("clarifications.clarifications_view"))

    if contents is None:
        error = "Failed to add clarification due to undefined contents."
        current_app.logger.info(error)
        flash(error, "danger")
        return redirect(url_for("clarifications.clarifications_view"))

    if (
        problem_input is None
    ):  # We check the problem input here because we can have a general clarification that would be a null problem in the database
        error = "Failed to add clarification due to undefined problem."
        current_app.logger.info(error)
        flash(error, "danger")
        return redirect(url_for("clarifications.clarifications_view"))

    problem = model.Problem.query.filter_by(name=problem_input).first()
    clar = model.Clarification(problem, current_user, subject, contents, False)
    db_session.add(clar)
    db_session.commit()

    return redirect(url_for("clarifications.clarifications_view"))


def answer_clar():
    """
    Answers a clarification

    Note:
        must be called from within a request context

    Returns:
        a redirect to the clarification view page
    """

    problem_name = request.form.get("problem")
    problem = model.Problem.query.filter_by(name=problem_name).first()
    subject = request.form.get("subject")
    contents = request.form.get("contents")
    answer = request.form.get("answer")
    is_public = request.form.get("is_public")
    publicity = False

    if subject is None:
        error = "Failed to answer clarification due to undefined subject."
        current_app.logger.info(error)
        flash(error, "danger")
        return redirect(url_for("clarifications.clarifications_view"))

    if contents is None:
        error = "Failed to answer clarification due to undefined contents."
        current_app.logger.info(error)
        flash(error, "danger")
        return redirect(url_for("clarifications.clarifications_view"))

    if problem is None:
        error = "Failed to answer clarification due to undefined problem."
        current_app.logger.info(error)
        flash(error, "danger")
        return redirect(url_for("clarifications.clarifications_view"))

    if answer is None:
        error = "Failed to answer clarification due to undefined answer."
        current_app.logger.info(error)
        flash(error, "danger")
        return redirect(url_for("clarifications.clarifications_view"))

    if is_public is not None:
        publicity = True

    clar = model.Clarification.query.filter_by(
        problem=problem, subject=subject, contents=contents
    ).first()
    clar.answer = answer
    clar.is_public = publicity
    db_session.commit()

    return redirect(url_for("clarifications.clarifications_view"))
