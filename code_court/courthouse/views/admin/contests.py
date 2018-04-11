import util

from sqlalchemy.exc import IntegrityError

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

contests = Blueprint(
    'contests', __name__, template_folder='templates/contests')


@contests.route("/", methods=["GET"], defaults={'page': 1})
@contests.route("/<int:page>", methods=["GET"])
@util.login_required("operator")
def contests_view(page):
    """
    The contest view page

    Returns:
        a rendered contest view template
    """
    contests = util.paginate(model.Contest.query, page, 30)

    return render_template("contests/view.html", contests=contests)


@contests.route(
    "/add/", methods=["GET", "POST"], defaults={'contest_id': None})
@contests.route("/edit/<int:contest_id>/", methods=["GET"])
@util.login_required("operator")
def contests_add(contest_id):
    """
    Displays the contest adding and updating page and accepts form submits from those pages.

    Params:
        contest_id (int): the contest to edit, if this is None a new contest will be made

    Returns:
        a rendered add/edit template or a redirect to the contest view page
    """
    if request.method == "GET":  # display add form
        return display_contest_add_form(contest_id)
    elif request.method == "POST":  # process added/edited contest
        return add_contest()
    else:
        current_app.logger.info("invalid contest add request method: %s",
                                request.method)
        abort(400)


@contests.route("/del/<contest_id>/", methods=["GET"])
@util.login_required("operator")
def contests_del(contest_id):
    """
    Deletes a contest

    Params:
        contest_id (int): the contest to delete

    Returns:
        a redirect to the contest view page
    """
    contest = model.Contest.query.filter_by(id=int(contest_id)).scalar()
    if contest is None:
        error = "Failed to delete contest \'{}\' as it doesn't exist.".format(
            contest.name)
        current_app.logger.info(error)
        flash(error, "danger")
        return redirect(url_for("contests.contests_view"))

    try:
        db_session.delete(contest)
        db_session.commit()
        flash("Deleted contest \'{}\'".format(contest.name), "warning")
    except IntegrityError:
        db_session.rollback()
        error = "Failed to delete contest \'{}\' as it's referenced in another DB element".format(
            contest.name)
        current_app.logger.info(error)
        flash(error, "danger")

    return redirect(url_for("contests.contests_view"))


def users_from_emails(emails, model):
    users = []

    for email in emails:
        db_user = model.User.query.filter_by(email=email).scalar()
        if db_user:
            users.append(db_user)
    return users


def problems_from_slugs(problem_slugs, model):
    problems = []

    for slug in problem_slugs:
        db_problem = model.Problem.query.filter_by(slug=slug).scalar()
        if db_problem:
            problems.append(db_problem)
    return problems


def add_contest():
    """
    Adds or edits a contest

    Note:
        must be called from within a request context

    Returns:
        a redirect to the contest view page
    """
    name = request.form.get("name")
    activate_date = request.form.get("activate_date")
    activate_time = request.form.get("activate_time")
    start_date = request.form.get("start_date")
    start_time = request.form.get("start_time")
    freeze_date = request.form.get("freeze_date")
    freeze_time = request.form.get("freeze_time")
    end_date = request.form.get("end_date")
    end_time = request.form.get("end_time")
    deactivate_date = request.form.get("deactivate_date")
    deactivate_time = request.form.get("deactivate_time")
    is_public = request.form.get("is_public")
    user_emails = request.form.get("users")
    problem_slugs = request.form.get("problems")

    if activate_date is not "" and activate_time is not "":
        activate_date_time = util.strs_to_dt(activate_date, activate_time)
    else:
        activate_date_time = None

    if freeze_date is not "" and freeze_time is not "":
        freeze_date_time = util.strs_to_dt(freeze_date, freeze_time)
    else:
        freeze_date_time = None

    if deactivate_date is not "" and deactivate_time is not "":
        deactivate_date_time = util.strs_to_dt(deactivate_date,
                                                deactivate_time)
    else:
        deactivate_date_time = None

    if name is None:
        error = "Failed to add contest due to undefined contest name."
        current_app.logger.info(error)
        flash(error, "danger")
        return redirect(url_for("contests.contests_view"))

    # convert is_public to a bool
    is_public_bool = util.checkbox_result_to_bool(is_public)
    if is_public_bool is None:
        error = "Failed to add contest \'{}\' due to invalid is_public check.".format(
            name)
        current_app.logger.info(error)
        flash(error, "danger")
        return redirect(url_for("contests.contests_view"))

    contest_id = util.i(request.form.get('contest_id'))
    if contest_id:  # edit
        contest = model.Contest.query.filter_by(id=int(contest_id)).one()
        contest.name = name
        contest.is_public = is_public_bool

        contest.activate_time = activate_date_time
        contest.start_time = util.strs_to_dt(start_date, start_time)
        contest.freeze_time = freeze_date_time
        contest.end_time = util.strs_to_dt(end_date, end_time)
        contest.deactivate_time = deactivate_date_time

        contest.users = users_from_emails(user_emails.split(), model)
        contest.problems = problems_from_slugs(problem_slugs.split(), model)
    else:  # add
        if is_dup_contest_name(name):
            error = "Failed to add contest \'{}\' as contest already exists.".format(
                name)
            current_app.logger.info(error)
            flash(error, "danger")
            return redirect(url_for("contests.contests_view"))

        contest = model.Contest(
            name=name,
            is_public=is_public_bool,
            activate_time=activate_date_time,
            start_time=util.strs_to_dt(start_date, start_time),
            freeze_time=freeze_date_time,
            end_time=util.strs_to_dt(end_date, end_time),
            deactivate_time=deactivate_date_time,
            users=users_from_emails(user_emails.split(), model),
            problems=problems_from_slugs(problem_slugs.split(), model))
        db_session.add(contest)

    db_session.commit()

    # If a problem is added to a contest, the cached runs will be
    # inaccurate. Clear the run cache to fix this.
    util.invalidate_cache(util.RUN_CACHE_NAME)

    return redirect(url_for("contests.contests_view"))


def display_contest_add_form(contest_id):
    """
    Displays the contest add template

    Params:
        contest_id (int): contest_id

    Returns:
        a rendered contest add/edit template
    """
    if contest_id is None:  # add
        return render_template(
            "contests/add_edit.html",
            action_label="Add",
            contest=None,
            user_emails=[user.email for user in model.User.query.all()],
            problem_slugs=[a.slug for a in model.Problem.query.all()])
    else:  # edit
        contest = model.Contest.query.filter_by(id=util.i(contest_id)).scalar()
        if contest is None:
            error = "Failed to edit contest \'{}\' as contest doesn't exist.".format(
                contest_id)
            current_app.logger.info(error)
            flash(error, "danger")
            return redirect(url_for("contests.contests_view"))

        return render_template(
            "contests/add_edit.html",
            action_label="Edit",
            contest=contest,
            user_emails=[user.email for user in model.User.query.all()],
            problem_slugs=[a.slug for a in model.Problem.query.all()])


# Util functions
def is_dup_contest_name(name):
    """
    Checks if a name is a duplicate of another contest

    Params:
        name (str): the contest name to test

    Returns:
        bool: True if the name is a duplicate, False otherwise
    """
    dup_contest = model.Contest.query.filter_by(name=name).scalar()
    if dup_contest:
        return True
    else:
        return False

