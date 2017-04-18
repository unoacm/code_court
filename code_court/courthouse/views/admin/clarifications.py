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

clarifications = Blueprint('clarifications', __name__,
                  template_folder='templates/clarifications')

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
    model = util.get_model()

    clarifications = model.Clarification.query.all()

    return render_template("clarifications/view.html", clarifications=clarifications)

@clarifications.route("/add/", methods=["GET", "POST"])
#@languages.route("/edit/<int:clar_id>/", methods=["GET"])
@util.login_required("operator")
def clarifications_add():
    """
    Displays the clarification adding and updating page and accepts form submits from those pages.

    Params:
        clar_id (int): the clarification to edit, if this is None a new lang will be made

    Returns:
        a rendered add/edit template or a redirect to the clarification view page
    """
    model = util.get_model()
    if request.method == "GET": # display add form
        return render_template("clarifications/add.html", action_label="Add")
#    elif request.method == "POST": # process added/edited lang
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
    model = util.get_model()

    clar = model.Clarification.query.filter_by(id=clar_id).scalar()
    if clar is None:
        current_app.logger.info("Can't delete clarification \'%d\' as it doesn't exist", clar.id)
        flash("Could not delete clarification \'{}\' as it does not exist.".format(clar.id), "danger")
        return redirect(url_for("clarifications.clarifications_view"))

    try:
        model.db.session.delete(clar)
        model.db.session.commit()
        flash("Deleted clarification \'{}\'".format(clar.id), "warning")
    except IntegrityError:
        model.db.session.rollback()
        current_app.logger.info("IntegrityError: Could not delete clarification \'{}\'.".format(clar.id))
        flash("IntegrityError: Could not delete clarification \'{}\' as it is referenced in another element in the database.".format(clar.id), "danger")

    return redirect(url_for("clarifications.clarifications_view"))


def add_clar():
    """
    Adds or edits a clarification

    Note:
        must be called from within a request context

    Returns:
        a redirect to the clarification view page
    """
    model = util.get_model()

    subject = request.form.get("subject")
    contents = request.form.get("contents")

    if subject is None:
        # TODO: give better feedback for failure
        current_app.logger.info("Undefined subject when trying to add clarification")
        abort(400)


    if contents is None:
        # TODO: give better feedback for failure
        current_app.logger.info("Undefined contents when trying to add clarification")
        abort(400)

    thread = str(uuid.uuid4())
    is_public = True #This is a general clarification, which are always public
    clar = model.Clarification(current_user, subject, contents, thread, is_public)
    model.db.session.add(clar)
    model.db.session.commit()

    return redirect(url_for("clarifications.clarifications_view"))
