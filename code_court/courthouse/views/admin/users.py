import util

from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

import paginate_sqlalchemy

from flask_login import current_user

from flask import (
    abort,
    Blueprint,
    current_app,
    render_template,
    redirect,
    request,
    url_for,
    flash, )

import model
from database import db_session

users = Blueprint('users', __name__, template_folder='templates/users')


@users.route("/", methods=["GET"], defaults={'page': 1})
@users.route("/<int:page>", methods=["GET"])
@util.login_required("operator")
def users_view(page):
    """
    The user view page

    Returns:
        a rendered user view template
    """
    user_search = request.args.get("search")
    user_role = request.args.get("user_role")

    users_query = model.User.query

    if user_search:
        term = '%' + user_search + '%'
        users_query = users_query.filter(
            or_(model.User.name.ilike(term), model.User.username.ilike(term)))
    if user_role and user_role != "all":
        users_query = users_query.join(model.User.user_roles).filter(
            model.UserRole.name == user_role)

    users_pagination = util.paginate(users_query, page, 30)
    users = users_pagination.items

    metrics = {}
    for user in users:
        user_metrics = {}

        run_query = model.Run.query.filter_by(user_id=user.id)

        user_metrics["num_runs"] = run_query.count()
        user_metrics["last_run"] = run_query.order_by(
            model.Run.submit_time.desc()).limit(1).first()

        metrics[user.id] = user_metrics

    return render_template(
        "users/view.html",
        users_pagination=users_pagination,
        users=users,
        metrics=metrics,
        user_role=user_role,
        search=user_search)


@users.route("/add/", methods=["GET", "POST"], defaults={'user_id': None})
@users.route("/edit/<int:user_id>/", methods=["GET"])
@util.login_required("operator")
def users_add(user_id):
    """
    Displays the user adding and updating page and accepts form submits from those pages.

    Params:
        user_id (int): the user to edit, if this is None a new user will be made

    Returns:
        a rendered add/edit template or a redirect to the user view page
    """
    if request.method == "GET":  # display add form
        return display_user_add_form(user_id)
    elif request.method == "POST":  # process added/edited user
        return add_user()
    else:
        current_app.logger.info("invalid user add request method: %s",
                                request.method)
        abort(400)


@users.route("/del/<user_id>/", methods=["GET"])
@util.login_required("operator")
def users_del(user_id):
    """
    Deletes a user

    Params:
        user_id (int): the user to delete

    Returns:
        a redirect to the user view page
    """
    user = model.User.query.filter_by(id=util.i(user_id)).scalar()

    if user is None:
        error = "Failed to delete user \'{}\' as it does not exist.".format(
            user_id)
        current_app.logger.info(error)
        flash(error, "danger")
        return redirect(url_for("users.users_view"))

    if current_user.id == user.id:
        error = "Failed to delete user \'{}\' because user cannot delete itself.".format(
            user_id)
        current_app.logger.info(error)
        flash(error, "danger")
        return redirect(url_for("users.users_view"))

    try:
        db_session.delete(user)
        db_session.commit()
        flash("Deleted user \'{}\'".format(user.username), "warning")
    except IntegrityError:
        db_session.rollback()
        error = "Failed to delete user \'{}\' as it's referenced in another DB element".format(
            user_id)
        current_app.logger.info(error)
        flash(error, "danger")

    return redirect(url_for("users.users_view"))


def add_user():
    """
    Adds or edits a user

    Note:
        must be called from within a request context

    Returns:
        a redirect to the user view page
    """
    user_id = request.form.get("user_id")
    name = request.form.get("name")
    username = request.form.get("username")
    password = request.form.get("password")
    confirm_password = request.form.get("confirm_password")
    misc_data = request.form.get("misc_data")
    contest_names = request.form.get("contest_names")
    user_roles = request.form.get("user_roles")

    if password != confirm_password:
        error = "Failed to add/edit \'{}\' due to password mismatch.".format(
            username)
        current_app.logger.info(error)
        flash(error, "danger")
        return redirect(url_for("users.users_view"))

    if user_id:  # edit
        user = model.User.query.filter_by(id=util.i(user_id)).one()
        user.name = name
        user.username = username
        if password != "":
            user.hashed_password = util.hash_password(password)
        user.misc_data = misc_data
        user.contests = retrieve_by_names(contest_names.split(), model.Contest)
        user.user_roles = retrieve_by_names(user_roles.split(),
                                            model.UserRole)
    else:  # add
        if is_dup_user_username(username):
            error = "Failed to add user \'{}\' as user already exists.".format(
                username)
            current_app.logger.info(error)
            flash(error, "danger")
            return redirect(url_for("users.users_view"))

        user = model.User(
            username=username,
            name=name,
            password=password,
            misc_data=misc_data,
            contests=retrieve_by_names(contest_names.split(), model.Contest),
            user_roles=retrieve_by_names(user_roles.split(), model.UserRole))
        db_session.add(user)

    db_session.commit()

    return redirect(url_for("users.users_view"))


def display_user_add_form(user_id):
    """
    Displays the user add template

    Params:
        user_id (int): user_id

    Returns:
        a rendered user add/edit template
    """
    if user_id is None:  # add
        return render_template(
            "users/add_edit.html", action_label="Add", user=None)
    else:  # edit
        user = model.User.query.filter_by(id=util.i(user_id)).scalar()
        if user is None:
            error = "Failed to edit user \'{}\' as user doesn't exist.".format(
                user_id)
            current_app.logger.info(error)
            flash(error, "danger")
            return redirect(url_for("users.users_view"))
        return render_template(
            "users/add_edit.html", action_label="Edit", user=user)


# Util functions
def is_dup_user_username(username):
    """
    Checks if a username is a duplicate of another user

    Params:
        username (str): the username to test

    Returns:
        bool: True if the username is a duplicate, False otherwise
    """
    return bool(model.User.query.filter_by(username=username).scalar())


def retrieve_by_ids(ids, table):
    """
    Retrieves a list of rows from the given table

    Params:
        ids (list): the ids of tuples to retrieve
        table     : the table to retrieve rows from

    Returns:
        list: the rows from the database
    """
    rows = []

    for id in ids:
        row = table.query.filter_by(id=util.i(id)).scalar()
        if row:
            rows.append(row)
    return rows


def retrieve_by_names(names, table):
    rows = []

    for name in names:
        row = table.query.filter_by(name=name).scalar()
        if row:
            rows.append(row)
    return rows

