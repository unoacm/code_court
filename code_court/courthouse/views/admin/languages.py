import json
import re

import util

from sqlalchemy.exc import IntegrityError

from flask_login import login_required

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

languages = Blueprint('languages', __name__,
                  template_folder='templates/language')

class ModelMissingException(Exception):
    pass

@languages.route("/", methods=["GET"], defaults={'page': 1})
@languages.route("/<int:page>", methods=["GET"])
@util.login_required("operator")
def languages_view(page):
    """
    The language view page

    Returns:
        a rendered language view template
    """
    model = util.get_model()

    languages = model.Language.query.paginate(page, 30)

    return render_template("language/view.html", languages=languages)

@languages.route("/add/", methods=["GET", "POST"], defaults={'lang_id': None})
@languages.route("/edit/<int:lang_id>/", methods=["GET"])
@util.login_required("operator")
def languages_add(lang_id):
    """
    Displays the language adding and updating page and accepts form submits from those pages.

    Params:
        lang_id (int): the lang to edit, if this is None a new lang will be made

    Returns:
        a rendered add/edit template or a redirect to the language view page
    """
    model = util.get_model()
    if request.method == "GET": # display add form
        return display_lang_add_form(lang_id)
    elif request.method == "POST": # process added/edited lang
        return add_lang()
    else:
        current_app.logger.info("invalid lang add request method: %s", request.method)
        abort(400)


@languages.route("/del/<lang_id>/", methods=["GET"])
@util.login_required("operator")
def languages_del(lang_id):
    """
    Deletes a language

    Params:
        lang_id (int): the language to delete

    Returns:
        a redirect to the language view page
    """
    model = util.get_model()

    lang = model.Language.query.filter_by(id=lang_id).scalar()
    if lang is None:
        error = "Failed to delete language \'{}\' as it does not exist.".format(lang_id)
        current_app.logger.info(error)
        flash(error, "danger")
        return redirect(url_for("languages.languages_view"))

    try:
        model.db.session.delete(lang)
        model.db.session.commit()
        flash("Deleted language \'{}\'".format(lang.name), "warning")
    except IntegrityError:
        model.db.session.rollback()
        error = "Failed to delete language \'{}\' as it's referenced in another DB element".format(lang_id)
        current_app.logger.info(error)
        flash(error, "danger")

    return redirect(url_for("languages.languages_view"))


def add_lang():
    """
    Adds or edits a language

    Note:
        must be called from within a request context

    Returns:
        a redirect to the language view page
    """
    model = util.get_model()

    name = request.form.get("name")
    syntax_mode = request.form.get("syntax_mode")
    is_enabled = request.form.get("is_enabled")
    run_script = request.form.get("run_script").replace('\r\n', '\n')

    if name is None:
        error = "Failed to add language due to undefined language name."
        current_app.logger.info(error)
        flash(error, "danger")
        return redirect(url_for("languages.languages_view"))

    if syntax_mode is None:
        error = "Failed to add language due to undefined syntax_mode."
        current_app.logger.info(error)
        flash(error, "danger")
        return redirect(url_for("languages.languages_view"))

    # convert is_enabled to a bool
    is_enabled_bool = util.checkbox_result_to_bool(is_enabled)
    if is_enabled_bool is None:
        error = "Failed to add language \'{}\' due to invalid is_enabled check.".format(name)
        current_app.logger.info(error)
        flash(error, "danger")
        return redirect(url_for("languages.languages_view"))

    lang_id = request.form.get('lang_id')
    if lang_id: # edit
        lang = model.Language.query.filter_by(id=lang_id).one()
        lang.name = name
        lang.syntax_mode = syntax_mode
        lang.is_enabled = is_enabled_bool
        lang.run_script = run_script
    else: # add
        if is_dup_lang_name(name):
            error = "Failed to add language \'{}\' as language already exists.".format(name)
            current_app.logger.info(error)
            flash(error, "danger")
            return redirect(url_for("languages.languages_view"))

        lang = model.Language(name, syntax_mode, is_enabled_bool, run_script)
        model.db.session.add(lang)

    model.db.session.commit()

    return redirect(url_for("languages.languages_view"))


def display_lang_add_form(lang_id):
    """
    Displays the language add template

    Params:
        lang_id (int): lang_id

    Returns:
        a rendered language add/edit template
    """
    model = util.get_model()

    if lang_id is None: # add
        return render_template("language/add_edit.html", action_label="Add")
    else: # edit
        lang = model.Language.query.filter_by(id=lang_id).scalar()
        if lang is None:
            error = "Failed to edit language \'{}\' as language doesn't exist.".format(lang_id)
            current_app.logger.info(error)
            flash(error, "danger")
            return redirect(url_for("languages.languages_view"))

        return render_template("language/add_edit.html",
                               action_label="Edit",
                               lang_id=lang_id,
                               name=lang.name,
                               syntax_mode=lang.syntax_mode,
                               is_enabled=lang.is_enabled,
                               run_script=lang.run_script)


## Util functions
def is_dup_lang_name(name):
    """
    Checks if a name is a duplicate of another lang

    Params:
        name (str): the lang name to test

    Returns:
        bool: True if the name is a duplicate, False otherwise
    """
    model = util.get_model()
    dup_lang = model.Language.query.filter_by(name=name).scalar()
    if dup_lang:
        return True
    else:
        return False
