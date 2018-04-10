import re
import zipfile

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

problems = Blueprint(
    'problems', __name__, template_folder='templates/problems')


@problems.route("/", methods=["GET"], defaults={'page': 1})
@problems.route("/<int:page>", methods=["GET"])
@util.login_required("operator")
def problems_view(page):
    """
    The problem view page

    Returns:
        a rendered problem view template
    """
    problems = util.paginate(model.Problem.query, page, 30)

    return render_template("problems/view.html", problems=problems)


def ini_to_dict(raw_ini):
    ini = {}
    for line in raw_ini.split("\n"):
        if line.strip() == "":
            continue

        keyval = re.match('\s*(\w+)\s*=\s*"(.*)"\s*', line)
        if keyval is None:
            keyval = re.match('\s*(\w+)\s*=\s*(.*)\s*', line)

        key, val = keyval.groups()

        ini[key] = val
    return ini


def extract_problem_data(problem_zip_file):
    problem_zip_file = zipfile.ZipFile(problem_zip_file)
    raw_ini = problem_zip_file.read("problem.ini").decode('utf-8')
    ini = ini_to_dict(raw_ini)
    data = {
        "slug":
        ini['short_name'],
        "name":
        ini['name'],
        "problem_statement":
        problem_zip_file.read("problem.md").decode('utf-8'),
        "sample_input":
        problem_zip_file.read("sample-input.txt").decode('utf-8'),
        "sample_output":
        problem_zip_file.read("sample-output.txt").decode('utf-8'),
        "secret_input":
        problem_zip_file.read("secret-input.txt").decode('utf-8'),
        "secret_output":
        problem_zip_file.read("secret-output.txt").decode('utf-8'),
    }
    return data


@problems.route("/batch_upload/", methods=["POST"])
@util.login_required("operator")
def problems_batch_upload():
    """
    Batch adds or updates problems from zip files.

    Params:
        None

    Returns:
        a redirect to the problem view page
    """
    if request.method == "POST":  # process added/edited problem
        input_output = model.ProblemType.query.filter_by(
            name="input-output").one()

        problem_zip_files = request.files.getlist("problems")

        for problem_zip_file in problem_zip_files:
            data = extract_problem_data(problem_zip_file)

            if is_dup_problem_slug(data['slug']):  # update
                problem = model.Problem.query.filter_by(
                    slug=data['slug']).one()
                problem.problem_type = input_output
                problem.name = data['name']
                problem.problem_statement = data['problem_statement']
                problem.sample_input = data['sample_input']
                problem.sample_output = data['sample_output']
                problem.secret_input = data['secret_input']
                problem.secret_output = data['secret_output']
            else:  # add
                problem = model.Problem(
                    problem_type=input_output,
                    slug=data['slug'],
                    name=data['name'],
                    problem_statement=data['problem_statement'],
                    sample_input=data['sample_input'],
                    sample_output=data['sample_output'],
                    secret_input=data['secret_input'],
                    secret_output=data['secret_output'])
                db_session.add(problem)

        db_session.commit()

        return redirect(url_for("problems.problems_view"))
    else:
        current_app.logger.info(
            "invalid problem batch upload request method: %s", request.method)
        abort(400)


@problems.route(
    "/add/", methods=["GET", "POST"], defaults={'problem_id': None})
@problems.route("/edit/<int:problem_id>/", methods=["GET"])
@util.login_required("operator")
def problems_add(problem_id):
    """
    Displays the problem adding and updating page and accepts form submits from those pages.

    Params:
        problem_id (int): the problem to edit, if this is None a new problem will be made

    Returns:
        a rendered add/edit template or a redirect to the problem view page
    """
    if request.method == "GET":  # display add form
        return display_problem_add_form(problem_id)
    elif request.method == "POST":  # process added/edited problem
        return add_problem()
    else:
        current_app.logger.info("invalid problem add request method: %s",
                                request.method)
        abort(400)


@problems.route("/del/<problem_id>/", methods=["GET"])
@util.login_required("operator")
def problems_del(problem_id):
    """
    Deletes a problem

    Params:
        problem_id (int): the problem to delete

    Returns:
        a redirect to the problem view page
    """
    problem = model.Problem.query.filter_by(id=int(problem_id)).scalar()
    if problem is None:
        error = "Failed to delete problem \'{}\' as it doesn't exist.".format(
            problem.slug)
        current_app.logger.info(error)
        flash(error, "danger")
        return redirect(url_for("problems.problems_view"))

    try:
        db_session.delete(problem)
        db_session.commit()
        flash("Deleted problem \'{}\'".format(problem.slug), "warning")
    except IntegrityError:
        db_session.rollback()
        error = "Failed to delete problem \'{}\' as it's referenced in another DB element".format(
            problem.slug)
        current_app.logger.info(error)
        flash(error, "danger")

    return redirect(url_for("problems.problems_view"))


def add_problem():
    """
    Adds or edits a problem

    Note:
        must be called from within a request context

    Returns:
        a redirect to the problem view page
    """
    problem_type_id = request.form.get("problem_type_id")
    problem_type = model.ProblemType.query.filter_by(
        id=int(problem_type_id)).one()
    slug = request.form.get("slug")
    name = request.form.get("name")
    is_enabled = request.form.get("is_enabled")
    problem_statement = request.form.get("problem_statement")
    sample_input = request.form.get("sample_input")
    sample_output = request.form.get("sample_output")
    secret_input = request.form.get("secret_input")
    secret_output = request.form.get("secret_output")

    if problem_type is None:
        error = "Failed to add problem due to undefined problem_type."
        current_app.logger.info(error)
        flash(error, "danger")
        return redirect(url_for("problems.problems_view"))

    if name is None:
        error = "Failed to add problem due to undefined problem name."
        current_app.logger.info(error)
        flash(error, "danger")
        return redirect(url_for("problems.problems_view"))

    is_enabled_bool = util.checkbox_result_to_bool(is_enabled)
    if is_enabled_bool is None:
        error = "Failed to add problem \'{}\' due to invalid is_enabled check.".format(
            name)
        current_app.logger.info(error)
        flash(error, "danger")
        return redirect(url_for("problems.problems_view"))

    if slug is None:
        error = "Failed to add problem due to undefined problem slug."
        current_app.logger.info(error)
        flash(error, "danger")
        return redirect(url_for("problems.problems_view"))

    problem_id = request.form.get('problem_id')
    if problem_id:  # edit
        problem = model.Problem.query.filter_by(id=int(problem_id)).one()
        problem.problem_type = problem_type
        problem.slug = slug
        problem.name = name
        problem.is_enabled = is_enabled_bool
        problem.problem_statement = problem_statement
        problem.sample_input = sample_input
        problem.sample_output = sample_output
        problem.secret_input = secret_input
        problem.secret_output = secret_output
    else:  # add
        # check if is duplicate
        if is_dup_problem_slug(slug):
            error = "Failed to add problem \'{}\' as problem already exists.".format(
                slug)
            current_app.logger.info(error)
            flash(error, "danger")
            return redirect(url_for("problems.problems_view"))

        problem = model.Problem(problem_type, slug, name, problem_statement,
                                sample_input, sample_output, secret_input,
                                secret_output)
        problem.is_enabled = is_enabled_bool
        db_session.add(problem)

    db_session.commit()

    util.invalidate_cache(util.RUN_CACHE_NAME)

    return redirect(url_for("problems.problems_view"))


def display_problem_add_form(problem_id):
    """
    Displays the problem add template

    Params:
        problem_id (int): problem_id

    Returns:
        a rendered problem add/edit template
    """
    problemtypes = model.ProblemType.query.all()

    if problem_id is None:  # add
        return render_template(
            "problems/add_edit.html",
            action_label="Add",
            problem=None,
            problemtypes=problemtypes)
    else:  # edit
        problem = model.Problem.query.filter_by(id=int(problem_id)).scalar()
        if problem is None:
            error = "Failed to edit problem \'{}\' as problem doesn't exist.".format(
                problem_id)
            current_app.logger.info(error)
            flash(error, "danger")
            return redirect(url_for("problems.problems_view"))

        return render_template(
            "problems/add_edit.html",
            action_label="Edit",
            problem=problem,
            problemtypes=problemtypes)


# Util functions
def is_dup_problem_slug(slug):
    """
    Checks if a slug is a duplicate of another problem

    Params:
        slug (str): the problem slug to test

    Returns:
        bool: True if the slug is a duplicate, False otherwise
    """
    dup_problem = model.Problem.query.filter_by(slug=slug).scalar()
    if dup_problem:
        return True
    else:
        return False

