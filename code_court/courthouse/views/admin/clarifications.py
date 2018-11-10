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
    Displays the clarification adding and updating page and accepts form submits from those pages

    Returns:
        a rendered add template or a redirect to the clarification view page
    """
    if request.method == "GET":  # display add form
        problems = model.Problem.query.all()
        return render_template("clarifications/add.html", action_label="Add", problems=problems)

    #    elif request.method == "POST": # process added lang
    elif request.method == "POST":
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
    """Displays the clarification answering page

    Params:
       clar_id (int): the clarification to view/answer

    Returns:
        a rendered answer page or a redirect to the clarification view page
    """

    if request.method == "GET":  # display answer form
        clarification = model.Clarification.query.filter_by(id=clar_id).first()
        return render_template("clarifications/answer.html", clarification=clarification)

    elif request.method == "POST": #clarification answered
        return answer_clar()
    else:
        current_app.logger.info("invalid clar add request method: %s", request.method)
        abort(400)


def answer_clar():
    """
    Answers the clarification

    Note:
        must be called from within a request context

    Returns:
        a redirect to the clarification view page
    """
    subject = request.form.get("subject")
    contents = request.form.get("contents")
    problem_name = request.form.get("problem")
    problem = model.Problem.query.filter_by(name=problem_name).first()
    answer = request.form.get("answer")
    is_public = request.form.get("is_public")

    if subject is None:
        error = "Failed to answer clarification due to undefined subject."
        current_app.logger.info(error)
        flash(error, "danger")
    elif contents is None:
        error = "Failed to answer clarification due to undefined contents."
        current_app.logger.info(error)
        flash(error, "danger")
    elif problem is None:
        error = "Failed to answer clarification due to undefined problem."
        current_app.logger.info(error)
        flash(error, "danger")
    elif answer is None:
        error = "Failed to answer clarification due to undefined answer."
        current_app.logger.info(error)
        flash(error, "danger")
    else:
        is_public_bool = util.checkbox_result_to_bool(is_public)
        clarification = model.Clarification.query.filter(problem==problem).filter(subject==subject).first()
        clarification.answer = answer
        clarification.answer_time = datetime.datetime.utcnow()
        clarification.is_public = is_public_bool
        db_session.commit()

    return redirect(url_for("clarifications.clarifications_view"))

def add_clar():
    """Adds a new clarification

    Note:
        must be called from within a request context

    Returns:
        a redicrect to the clarification view page
    """

    subject = request.form.get("subject")
    contents = request.form.get("contents")
    problem_name = request.form.get("problem")
    problem = model.Problem.query.filter_by(name=problem_name).first()

    if subject is None:
        error = "Failed to add clarification due to undefined subject."
        current_app.logger.info(error)
        flash(error, "danger")
    elif contents is None:
        error = "Failed to add clarification due to undefined contents."
        current_app.logger.info(error)
        flash(error, "danger")
    elif problem is None:
        error = "Failed to add clarification due to undefined problem."
        current_app.logger.info(error)
        flash(error, "danger")
    else:
        clarification = model.Clarification(
                problem,
                current_user,
                subject,
                contents,
                False
        )

        db_session.add(clarification)
        db_session.commit()

    return redirect(url_for("clarifications.clarifications_view"))

