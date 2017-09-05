import util

from flask import (
    abort,
    Blueprint,
    current_app,
    render_template,
    redirect,
    request,
    url_for,
    flash, )

configurations = Blueprint(
    'configurations', __name__, template_folder='templates/configurations')


@configurations.route("/", methods=["GET", "POST"], defaults={'page': 1})
@configurations.route("/<int:page>", methods=["GET", "POST"])
@util.login_required("operator")
def configurations_view(page):
    """
    The config view page

    Returns:
        a rendered config view template
    """
    model = util.get_model()

    config_query = model.Configuration.query

    configs = config_query.order_by(
        model.Configuration.category.asc()).paginate(page, 30)

    return render_template("configurations/view.html", configs=configs)


@configurations.route(
    "/add/", methods=["GET", "POST"], defaults={'config_id': None})
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
    if request.method == "GET":  # display add form
        return display_config_add_form(config_id)
    elif request.method == "POST":  # process added/edited config
        return add_config()
    else:
        current_app.logger.info("invalid config add request method: %s",
                                request.method)
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

    config = model.Configuration.query.filter_by(id=int(config_id)).scalar()

    if config is None:
        error = "Failed to delete config \'{}\' as config doesn't exist.".format(
            config_id)
        current_app.logger.info(error)
        flash(error, "danger")
        return redirect(url_for("configurations.configurations_view"))

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
    category = request.form.get("category")

    if config_id:  # edit
        config = model.Configuration.query.filter_by(id=int(config_id)).one()
        config.key = key
        config.val = val
        config.valType = valType
        config.category = category
    else:  # add
        if is_dup_config_key(key):
            error = "Failed to add config \'{}\' as config already exists.".format(
                key)
            current_app.logger.info(error)
            flash(error, "danger")
            return redirect(url_for("configurations.configurations_view"))

        config = model.Configuration(
            key=key, val=val, valType=valType, category=category)
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

    if config_id is None:  # add
        return render_template(
            "configurations/add_edit.html", action_label="Add", config=None)
    else:  # edit
        config = model.Configuration.query.filter_by(
            id=int(config_id)).scalar()
        if config is None:
            error = "Failed to edit config \'{}\' as config doesn't exist.".format(
                config_id)
            current_app.logger.info(error)
            flash(error, "danger")
            return redirect(url_for("configurations.configurations_view"))

        return render_template(
            "configurations/add_edit.html", action_label="Edit", config=config)


# Util functions
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

