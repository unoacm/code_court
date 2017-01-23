import json
import re

from flask import (
    abort,
    Blueprint,
    current_app,
    render_template,
    redirect,
    request,
    url_for,
)

admin = Blueprint('admin', __name__,
                        template_folder='templates')

class ModelMissingException(Exception):
    pass

@admin.route("/", methods=["GET"])
def index():
    """
    The index page for the admin interface, contains
    a list of links to other admin pages
    """
    return render_template("admin_index.html")

@admin.route("/users/", methods=["GET"])
def users():
    """
    The user view page
    """
    return render_template("users.html")

@admin.route("/languages/", methods=["GET"])
def languages_view():
    """
    The language view page
    """
    model = current_app.config.get('model')
    if model is None:
        raise ModelMissingException()

    languages = model.Language.query.all()

    return render_template("language/view.html", languages=languages)

@admin.route("/languages/add/", methods=["GET", "POST"])
def languages_add():
    """
    The language adding page
    """
    if request.method == "GET":
        return render_template("language/add.html", action_label="Add")
    elif request.method == "POST":
        model = current_app.config.get('model')
        if model is None:
            raise ModelMissingException()

        name = request.form.get("name")
        is_enabled = request.form.get("is_enabled")

        if name is None:
            # TODO: give better feedback for failure
            abort(400)

        # convert is_enabled to a bool
        if is_enabled == "on":
            is_enabled_bool = True
        elif is_enabled == "off" or is_enabled is None:
            is_enabled_bool = False
        else:
            # TODO: give better feedback for failure
            current_app.logger.info("Invalid language is_enabled: %s", is_enabled)
            abort(400)


        lang = model.Language(name, is_enabled_bool)
        model.db.session.add(lang)
        model.db.session.commit()

        return redirect(url_for("admin.languages_view"))

@admin.route("/languages/del/<lang_id>", methods=["GET"])
def languages_del(lang_id):
    """
    The language deleting page
    """
    model = current_app.config.get('model')
    if model is None:
        raise ModelMissingException()

    lang = model.Language.query.filter_by(id=lang_id).one()
    model.db.session.delete(lang)
    model.db.session.commit()

    return redirect(url_for("admin.languages_view"))
