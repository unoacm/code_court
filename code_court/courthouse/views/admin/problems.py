import json
import re
import sqlalchemy

import util

from sqlalchemy.exc import IntegrityError

from flask_login import login_required

from flask import (
    abort,
    Blueprint,
    current_app,
    render_template,
    redirect,
    request,
    url_for,
    flash,
)

problems = Blueprint('problems', __name__,
                  template_folder='templates/problems')

@problems.route("/", methods=["GET"], defaults={'page': 1})
@problems.route("/<int:page>", methods=["GET"])
@util.login_required("operator")
def problems_view(page):
    """
    The problem view page

    Returns:
        a rendered problem view template
    """
    model = util.get_model()

    problems = model.Problem.query.paginate(page, 30)

    return render_template("problems/view.html", problems=problems)

@problems.route("/add/", methods=["GET", "POST"], defaults={'problem_id': None})
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
    model = util.get_model()
    if request.method == "GET": # display add form
        return display_problem_add_form(problem_id)
    elif request.method == "POST": # process added/edited problem
        return add_problem()
    else:
        current_app.logger.info("invalid problem add request method: %s", request.method)
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
    model = util.get_model()

    problem = model.Problem.query.filter_by(id=problem_id).scalar()
    if problem is None:
        current_app.logger.info("Can't delete problem \'%s\' as it doesn't exist", problem.slug)
        flash("Could not delete problem \'{}\' as it does not exist.".format(problem.slug), "danger")
        abort(400)

    try:
        model.db.session.delete(problem)
        model.db.session.commit()
        flash("Deleted problem \'{}\'".format(problem.slug), "warning")
    except IntegrityError:
        model.db.session.rollback()
        current_app.logger.info("IntegrityError: Could not delete problem \'{}\'.".format(problem.slug))
        flash("IntegrityError: Could not delete problem \'{}\' as it is referenced in another element in the database.".format(problem.slug), "danger")

    return redirect(url_for("problems.problems_view"))

def add_problem():
    """
    Adds or edits a problem

    Note:
        must be called from within a request context

    Returns:
        a redirect to the problem view page
    """
    model = util.get_model()

    problem_type_id = request.form.get("problem_type_id")
    problem_type = model.ProblemType.query.filter_by(id=problem_type_id).one()
    slug = request.form.get("slug")
    name = request.form.get("name")
    problem_statement = request.form.get("problem_statement")
    sample_input = request.form.get("sample_input")
    sample_output = request.form.get("sample_output")
    secret_input = request.form.get("secret_input")
    secret_output = request.form.get("secret_output")

    if problem_type is None:
        # TODO: give better feedback for failure
        current_app.logger.info("Undefined problem_type when trying to add problem")
        abort(400)

    if name is None:
        # TODO: give better feedback for failure
        current_app.logger.info("Undefined name when trying to add problem")
        abort(400)

    problem_id = request.form.get('problem_id')
    if problem_id: # edit
        problem = model.Problem.query.filter_by(id=problem_id).one()
        problem.problem_type = problem_type
        problem.slug = slug
        problem.name = name
        problem.problem_statement = problem_statement
        problem.sample_input = sample_input
        problem.sample_output = sample_output
        problem.secret_input = secret_input
        problem.secret_output = secret_output
    else: # add
        # check if is duplicate
        if is_dup_problem_slug(slug):
            # TODO: give better feedback for failure
            current_app.logger.info("Tried to add a duplicate problem: %s", slug)
            abort(400)

        problem = model.Problem(problem_type,
                                slug,
                                name,
                                problem_statement,
                                sample_input,
                                sample_output,
                                secret_input,
                                secret_output)
        model.db.session.add(problem)

    model.db.session.commit()

    return redirect(url_for("problems.problems_view"))



def display_problem_add_form(problem_id):
    """
    Displays the problem add template

    Params:
        problem_id (int): problem_id

    Returns:
        a rendered problem add/edit template
    """
    model = util.get_model()
    problemtypes = model.ProblemType.query.all()

    if problem_id is None: # add
        return render_template("problems/add_edit.html",
                               action_label="Add",
                               problem=None,
                               problemtypes=problemtypes)
    else: # edit
        problem = model.Problem.query.filter_by(id=problem_id).scalar()
        if problem is None:
            # TODO: give better feedback for failure
            current_app.logger.info("Tried to edit non-existant problem, id:%s", problem_id)
            abort(400)
        return render_template("problems/add_edit.html",
                               action_label="Edit",
                               problem=problem,
                               problemtypes=problemtypes)


## Util functions
def is_dup_problem_slug(slug):
    """
    Checks if a slug is a duplicate of another problem

    Params:
        slug (str): the problem slug to test

    Returns:
        bool: True if the slug is a duplicate, False otherwise
    """
    model = util.get_model()
    dup_problem = model.Problem.query.filter_by(slug=slug).scalar()
    if dup_problem:
        return True
    else:
        return False

