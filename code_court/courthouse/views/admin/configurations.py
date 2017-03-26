import collections
import json
import re
import sqlalchemy

import util

from sqlalchemy import or_

from flask_login import login_required

from flask import (
    abort,
    Blueprint,
    current_app,
    render_template,
    redirect,
    request,
    url_for,
)

configurations = Blueprint('configurations', __name__,
                  template_folder='templates/configurations')

@configurations.route("/", methods=["GET", "POST"])
@util.login_required("operator")
def configurations_view():
    """
    The config view page

    Returns:
        a rendered config view template
    """
    model = util.get_model()

    configs = model.Configuration.query.all()

    return render_template("configurations/view.html", configs=configs)


@configurations.route("/add/", methods=["GET", "POST"], defaults={'config_id': None})
@configurations.route("/edit/<int:config_id>/", methods=["GET"])
@util.login_required("operator")
def configurations_add(config_id):
    """
    Displays the config adding and updating page and accepts form submits from those pages.

    Params:
        config_id (int): the config to edit, if this is None a new config will be made

    Returns:
        a rendered add/edit template or a redirect to the config view page
    """
    model = util.get_model()
    if request.method == "GET": # display add form
        return display_config_add_form(config_id)
    elif request.method == "POST": # process added/edited config
        return add_config()
    else:
        current_app.logger.info("invalid config add request method: %s", request.method)
        abort(400)


@configurations.route("/del/<config_id>/", methods=["GET"])
@util.login_required("operator")
def configurations_del(config_id):
    """
    Deletes a config

    Params:
        config_id (int): the config to delete

    Returns:
        a redirect to the config view page
    """
    model = util.get_model()

    config = model.Configuration.query.filter_by(id=config_id).scalar()

    if config is None:
        current_app.logger.info("Can't delete config %s, doesn't exist", config_id)
        abort(400)

    model.db.session.delete(config)
    model.db.session.commit()

    return redirect(url_for("configurations.configurations_view"))


def add_config():
    """
    Adds or edits a config

    Note:
        must be called from within a request context

    Returns:
        a redirect to the config view page
    """
    model = util.get_model()

    config_id = request.form.get("config_id")
    key = request.form.get("key")
    val = request.form.get("val")
    valType = request.form.get("valType")

    if config_id: # edit
        config = model.Configuration.query.filter_by(id=config_id).one()
        config.key = key
        config.val = val
        config.valType = valType
    else: # add
        # check if is duplicate
        if is_dup_config_key(key):
            # TODO: give better feedback for failure
            current_app.logger.info("Tried to add a duplicate config: %s", key)
            abort(400)

        config = model.Configuration(key=key,
                                     val=val,
                                     valType=valType)
        model.db.session.add(config)

    model.db.session.commit()

    return redirect(url_for("configurations.configurations_view"))


def display_config_add_form(config_id):
    """
    Displays the config add template

    Params:
        config_id (int): config_id

    Returns:
        a rendered config add/edit template
    """
    model = util.get_model()

    if config_id is None: # add
        return render_template("configurations/add_edit.html",
                               action_label="Add",
                               config=None)
    else: # edit
        config = model.Configuration.query.filter_by(id=config_id).scalar()
        if config is None:
            # TODO: give better feedback for failure
            current_app.logger.info("Tried to edit non-existant config, id:%s", config_id)
            abort(400)
        return render_template("configurations/add_edit.html",
                               action_label="Edit",
                               config=config)


## Util functions
def is_dup_config_key(key):
    """
    Checks if a key is a duplicate of another config

    Params:
        key (str): the config key to test

    Returns:
        bool: True if the email is a duplicate, False otherwise
    """
    model = util.get_model()
    dup_config = model.Configuration.query.filter_by(key=key).scalar()
    if dup_config:
        return True
    else:
        return False


