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

users = Blueprint('users', __name__,
                  template_folder='templates/users')

@users.route("/", methods=["GET", "POST"])
@util.login_required("operator")
def users_view():
    """
    The user view page

    Returns:
        a rendered user view template
    """
    model = util.get_model()

    user_search = request.form.get("search")
    user_role = request.form.get("user_role")

    if user_search is not None:
        term = '%' + user_search + '%'
        user_query = model.User.query.filter(or_(model.User.name.ilike(term), 
                                                 model.User.email.ilike(term)))
    else:
        user_query = model.User.query.all()

    if user_role is None or user_role == "all":
        users = user_query
    else:
        users = []
        for user in user_query:
            for role in user.user_roles:
                if role.id == user_role:
                    users.append(user)

    metrics = collections.OrderedDict() 
    for user in users:
        user_metrics = collections.OrderedDict()
         
        run_query = model.Run.query.filter_by(user_id=user.id)
        runs = run_query.order_by(model.Run.submit_time.desc()).all()
        
        user_metrics["num_runs"] = len(runs)

        if len(runs) != 0:
            user_metrics["last_submit_time"] = runs[0].submit_time

        metrics[user.id] = user_metrics

    return render_template("users/view.html", users=users,
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
    model = util.get_model()
    if request.method == "GET": # display add form
        return display_user_add_form(user_id)
    elif request.method == "POST": # process added/edited user
        return add_user()
    else:
        current_app.logger.info("invalid user add request method: %s", request.method)
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
    model = util.get_model()

    users = model.User.query.filter_by(id=user_id).all()
    if len(users) == 0:
        current_app.logger.info("Can't delete user %s, doesn't exist", user_id)
        abort(400)

    model.db.session.delete(users[0])
    model.db.session.commit()

    return redirect(url_for("users.users_view"))


def add_user():
    """
    Adds or edits a user

    Note:
        must be called from within a request context

    Returns:
        a redirect to the user view page
    """
    model = util.get_model()

    user_id = request.form.get("user_id")
    email = request.form.get("email")
    name = request.form.get("name")
    password = request.form.get("password")
    misc_data = request.form.get("misc_data")
    contest_ids = request.form.get("contest_ids")
    user_role_ids = request.form.get("user_role_ids")

    if user_id: # edit
        user = model.User.query.filter_by(id=user_id).one()
        user.email = email
        user.name = name
        if password != "":
            user.hashed_password = util.hash_password(password)
        user.misc_data = misc_data
        user.contests = retrieve_by_ids(contest_ids.split(), model.Contest)
        user.user_roles = retrieve_by_ids(user_role_ids.split(), model.UserRole)
    else: # add
        # check if is duplicate
        if is_dup_user_email(email):
            # TODO: give better feedback for failure
            current_app.logger.info("Tried to add a duplicate user: %s", email)
            abort(400)

        user = model.User(email=email,
                            name=name,
                            password=password,
                            misc_data=misc_data,
                            contests=retrieve_by_ids(contest_ids.split(), model.Contest),
                            user_roles=retrieve_by_ids(user_role_ids.split(), model.UserRole))
        model.db.session.add(user)

    model.db.session.commit()

    return redirect(url_for("users.users_view"))


def display_user_add_form(user_id):
    """
    Displays the user add template

    Params:
        user_id (int): user_id

    Returns:
        a rendered user add/edit template
    """
    model = util.get_model()

    if user_id is None: # add
        return render_template("users/add_edit.html",
                               action_label="Add",
                               user=None)
    else: # edit
        users = model.User.query.filter_by(id=user_id).all()
        if len(users) == 0:
            # TODO: give better feedback for failure
            current_app.logger.info("Tried to edit non-existant user, id:%s", user_id)
            abort(400)
        return render_template("users/add_edit.html",
                               action_label="Edit",
                               user=users[0])


## Util functions
def is_dup_user_email(email):
    """
    Checks if an email is a duplicate of another user

    Params:
        email (str): the user name to test

    Returns:
        bool: True if the email is a duplicate, False otherwise
    """
    model = util.get_model()
    dup_user = model.User.query.filter_by(email=email).all()
    return len(dup_user) > 0


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
        row = table.query.filter_by(id=id).all()
        if len(row) != 0:
            rows.append(row[0])
    return rows

