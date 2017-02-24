import datetime
import json
import re
import sqlalchemy

import util

from flask import (
    abort,
    Blueprint,
    current_app,
    render_template,
    redirect,
    request,
    url_for,
)

contests = Blueprint('contests', __name__,
                  template_folder='templates/contests')

class ModelMissingException(Exception):
    pass

@contests.route("/", methods=["GET"])
def contests_view():
    """
    The contest view page

    Returns:
        a rendered contest view template
    """
    model = util.get_model()

    contests = model.Contest.query.all()

    return render_template("contests/view.html", contests=contests)

@contests.route("/add/", methods=["GET", "POST"], defaults={'contest_id': None})
@contests.route("/edit/<int:contest_id>/", methods=["GET"])
def contests_add(contest_id):
    """
    Displays the contest adding and updating page and accepts form submits from those pages.

    Params:
        contest_id (int): the contest to edit, if this is None a new contest will be made

    Returns:
        a rendered add/edit template or a redirect to the contest view page
    """
    model = util.get_model()
    if request.method == "GET": # display add form
        return display_contest_add_form(contest_id)
    elif request.method == "POST": # process added/edited contest
        return add_contest()
    else:
        current_app.logger.info("invalid contest add request method: %s", request.method)
        abort(400)


@contests.route("/del/<contest_id>/", methods=["GET"])
def contests_del(contest_id):
    """
    Deletes a contest

    Params:
        contest_id (int): the contest to delete

    Returns:
        a redirect to the contest view page
    """
    model = util.get_model()


    contests = model.Contest.query.filter_by(id=contest_id).all()
    if len(contests) == 0:
        current_app.logger.info("Can't delete contest %s, doesn't exist", contest_id)
        abort(400)

    model.db.session.delete(contests[0])
    model.db.session.commit()

    return redirect(url_for("contests.contests_view"))


def date_time_string_to_datetime(date_time_string):
    """Convert "2016-11-30 13:59:30" into datetime.datetime(2016, 11, 30, 13, 59, 30)"""
    date_string, time_string = date_time_string.split(" ")
    year, month, day = map(int, date_string.split("-"))
    hour, minute, second = map(int, time_string.split(":"))
    return datetime.datetime(year, month, day, hour, minute, second)


def users_from_emails(emails, model):
    users = []

    for email in emails:
        db_users = model.User.query.filter_by(email=email).all()
        if len(db_users) != 0:
            users.append(db_users[0])
    return users


def problems_from_names(problem_names, model):
    problems = []

    # Is this db querying problematic?
    for name in problem_names:
        db_problems = model.Problem.query.filter_by(name=name).all()
        if len(db_problems) != 0:
            problems.append(db_problems[0])
    return problems


def add_contest():
    """
    Adds or edits a contest

    Note:
        must be called from within a request context

    Returns:
        a redirect to the contest view page
    """
    model = util.get_model()

    name = request.form.get("name")
    activate_time = request.form.get("activate_time")
    start_time = request.form.get("start_time")
    freeze_time = request.form.get("freeze_time")
    end_time = request.form.get("end_time")
    deactivate_time = request.form.get("deactivate_time")
    is_public = request.form.get("is_public")
    user_emails = request.form.get("users")
    problem_names = request.form.get("problems")

    if name is None:
        # TODO: give better feedback for failure
        current_app.logger.info("Undefined name when trying to add contest")
        abort(400)

    # convert is_public to a bool

    is_public_bool = checkbox_result_to_bool(is_public)
    if is_public_bool is None:
        # TODO: give better feedback for failure
        current_app.logger.info("Invalid contest is_public: %s", is_public)
        abort(400)

    contest_id = request.form.get('contest_id')
    if contest_id: # edit
        contest = model.Contest.query.filter_by(id=contest_id).one()
        contest.name = name
        contest.is_public = is_public_bool

        contest.activate_time = date_time_string_to_datetime(activate_time)
        contest.start_time = date_time_string_to_datetime(start_time)
        contest.freeze_time = date_time_string_to_datetime(freeze_time)
        contest.end_time = date_time_string_to_datetime(end_time)
        contest.deactivate_time = date_time_string_to_datetime(deactivate_time)

        contest.users = users_from_emails(user_emails.split(), model)
        contest.problems = problems_from_names(problem_names.split(), model)
    else: # add
        # check if is duplicate
        if is_dup_contest_name(name):
            # TODO: give better feedback for failure
            current_app.logger.info("Tried to add a duplicate contest: %s", name)
            abort(400)

        contest = model.Contest(name=name,
                                is_public=is_public_bool,
                                activate_time = date_time_string_to_datetime(activate_time),
                                start_time = date_time_string_to_datetime(start_time),
                                freeze_time = date_time_string_to_datetime(freeze_time),
                                end_time = date_time_string_to_datetime(end_time),
                                deactivate_time = date_time_string_to_datetime(deactivate_time),
                                users = users_from_emails(user_emails.split(), model),
                                problems = problems_from_names(problem_names.split(), model))
        model.db.session.add(contest)

    model.db.session.commit()

    return redirect(url_for("contests.contests_view"))



def display_contest_add_form(contest_id):
    """
    Displays the contest add template

    Params:
        contest_id (int): contest_id

    Returns:
        a rendered contest add/edit template
    """
    model = util.get_model()

    if contest_id is None: # add
        return render_template("contests/add_edit.html", action_label="Add", contest=None,
                               user_emails=[user.email for user in model.User.query.all()],
                               problem_names=[a.name for a in model.Problem.query.all()])
    else: # edit
        contest_list = model.Contest.query.filter_by(id=contest_id).all()
        if len(contest_list) == 0:
            # TODO: give better feedback for failure
            current_app.logger.info("Tried to edit non-existant contest, id:%s", contest_id)
            abort(400)
        return render_template("contests/add_edit.html",
                               action_label="Edit",
                               contest=contest_list[0],
                               user_emails=[user.email for user in model.User.query.all()],
                               problem_names=[a.name for a in model.Problem.query.all()])



## Util functions
def get_model():
    """
    Gets the model from the current app,

    Note:
        must be called from within a request context

    Raises:
        ModelMissingException: if the model is not accessible from the current_app

    Returns:
        the model module
    """
    model = current_app.config.get('model')
    if model is None:
        raise ModelMissingException()
    return model


def is_dup_contest_name(name):
    """
    Checks if a name is a duplicate of another contest

    Params:
        name (str): the contest name to test

    Returns:
        bool: True if the name is a duplicate, False otherwise
    """
    model = util.get_model()
    dup_contest = model.Contest.query.filter_by(name=name).all()
    return len(dup_contest) > 0

def checkbox_result_to_bool(res):
    """
    Takes in a checkbox result from a form and converts it to a bool

    Params:
        res (str): the result string from a checkbox

    Returns:
        bool: the boolean value of res
    """
    if res == "on":
        return True
    elif res == "off" or res is None:
        return False
    return None
