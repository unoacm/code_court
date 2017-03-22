import json
import re

import util

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
)

languages = Blueprint('languages', __name__,
                  template_folder='templates/language')

class ModelMissingException(Exception):
    pass

@languages.route("/", methods=["GET"])
@util.login_required("operator")
def languages_view():
    """
    The language view page

    Returns:
        a rendered language view template
    """
    model = util.get_model()

    languages = model.Language.query.all()

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

    langs = model.Language.query.filter_by(id=lang_id).all()
    if len(langs) == 0:
        current_app.logger.info("Can't delete lang %s, doesn't exist", lang_id)
        abort(400)

    lang_name = langs[0].name
    model.db.session.delete(langs[0])
    model.db.session.commit()

    flash("Deleted language {}".format(lang_name), "warning")
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
    is_enabled = request.form.get("is_enabled")
    run_script = request.form.get("run_script")

    if name is None:
        # TODO: give better feedback for failure
        current_app.logger.info("Undefined name when trying to add language")
        abort(400)

    # convert is_enabled to a bool

    is_enabled_bool = util.checkbox_result_to_bool(is_enabled)
    if is_enabled_bool is None:
        # TODO: give better feedback for failure
        current_app.logger.info("Invalid language is_enabled: %s", is_enabled)
        abort(400)

    lang_id = request.form.get('lang_id')
    if lang_id: # edit
        lang = model.Language.query.filter_by(id=lang_id).one()
        lang.name = name
        lang.is_enabled = is_enabled_bool
        lang.run_script = run_script
    else: # add
        # check if is duplicate
        if is_dup_lang_name(name):
            # TODO: give better feedback for failure
            current_app.logger.info("Tried to add a duplicate language: %s", name)
            abort(400)

        lang = model.Language(name, is_enabled_bool, run_script)
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
        lang = model.Language.query.filter_by(id=lang_id).all()
        if len(lang) == 0:
            # TODO: give better feedback for failure
            current_app.logger.info("Tried to edit non-existant lang, id:%s", lang_id)
            abort(400)
        return render_template("language/add_edit.html",
                               action_label="Edit",
                               lang_id=lang_id,
                               name=lang[0].name,
                               is_enabled=lang[0].is_enabled,
                               run_script=lang[0].run_script)


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

