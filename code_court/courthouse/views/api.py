"""
Contains api endpoints for the defendant frontend
and external services
"""
import datetime
import json
import re

import six

import util

from flask_httpauth import HTTPBasicAuth
from flask_login import current_user, login_user, logout_user
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity


from flask import (
    abort,
    Blueprint,
    current_app,
    jsonify,
    make_response,
    render_template,
    request,
    url_for,
)

api = Blueprint('api', __name__,
                template_folder='templates')
executioner_auth = HTTPBasicAuth()

# api auth
@executioner_auth.verify_password
def verify_password(email, password):
    model = util.get_model()
    user = model.User.query.filter_by(email=email).first()
    if not user or not user.verify_password(password):
        return False
    return True

@executioner_auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)

# api routes
@api.route("/get-writ", methods=["GET"])
@executioner_auth.login_required
def get_writ():
    """endpoint for executioners to get runs to execute"""
    model = util.get_model()
    # choose the oldest run
    chosen_run = model.Run.query.filter_by(started_execing_time=None)\
                                          .order_by(model.Run.submit_time.asc()).first()
    if chosen_run is None:
        return make_response(jsonify({'status': 'unavailable'}), 404)

    # TODO: use a better locking method to prevent dual execution
    chosen_run.started_execing_time = datetime.datetime.utcnow()
    model.db.session.commit()

    resp = {
        "status": "found",
        "source_code": chosen_run.source_code,
        "language": chosen_run.language.name,
        "run_script": chosen_run.language.run_script,
        "input": chosen_run.run_input,
        "run_id": chosen_run.id,
        "return_url": url_for("api.submit_writ", run_id=chosen_run.id, _external=True)
    }

    return make_response(jsonify(resp), 200)

@api.route("/submit-writ/<run_id>", methods=["POST"])
@executioner_auth.login_required
def submit_writ(run_id):
    """endpoint for executioners to submit runs

    Looking for the format:
    {
        "output": "..."
    }
    """
    model = util.get_model()
    run = model.Run.query.filter_by(id=run_id).first()
    if not run:
        current_app.logger.debug("Received writ without valid run, id: %s", run_id)
        abort(404)

    if run.finished_execing_time:
        current_app.logger.warning("Received writ submission for already submitted run, id: %s", run_id)
        abort(400)

    if not request.json:
        current_app.logger.debug("Received writ without json")
        abort(400)

    if 'output' not in request.json or not isinstance(request.json['output'], six.string_types):
        current_app.logger.debug("Received writ without the output field")
        abort(400)

    run.run_output = request.json['output']
    run.finished_execing_time = datetime.datetime.utcnow()

    is_correct = clean_output_string(run.run_output) == clean_output_string(run.correct_output)
    run.is_passed = is_correct

    model.db.session.commit()
    return "Good"

@api.route("/return-without-run/<run_id>", methods=["POST"])
@executioner_auth.login_required
def return_without_run(run_id):
    """Allows for executors to return a writ without running if they are
    experiencing errors or are shutting down
    """
    model = util.get_model()
    run = model.Run.query.filter_by(id=run_id).first()
    if not run:
        current_app.logger.debug("Received writ without valid run, id: %s", run_id)
        abort(404)

    if run.finished_execing_time:
        current_app.logger.warning("Received return for already returned writ, id: %s", run_id)
        abort(400)

    run.started_execing_time = None
    model.db.session.commit()

    return "Good"

@api.route('/login', methods=['POST'])
def login():
    model = util.get_model()

    email = request.json.get('email', None)
    password = request.json.get('password', None)

    user = model.User.query.filter_by(email=email).scalar()

    if user and user.verify_password(password):
        ret = {'access_token': create_access_token(identity=user.id)}
        return jsonify(ret), 200
    else:
        return jsonify({"msg": "Bad username or password"}), 401

@api.route("/problem/<slug>", methods=["GET"])
def get_problem(slug):
    model = util.get_model()

    problem = model.Problem.query.filter_by(slug=slug).scalar()

    return make_response(jsonify(problem.get_output_dict()), 200)

@api.route("/problems", methods=["GET"])
@jwt_required
def get_all_problems():
    model = util.get_model()

    current_user_id = get_jwt_identity()
    current_user = model.User.query.filter_by(id=current_user_id).scalar()

    problems = model.Problem.query.all()

    resp = {}
    for problem in problems:
        problem_runs = model.Run.query.filter_by(user=current_user, problem=problem).all()
        problem_run_dicts = [x.get_output_dict() for x in problem_runs]

        problem_dict = problem.get_output_dict()
        problem_dict['runs'] = problem_run_dicts

        resp[problem.slug] = problem_dict

    return make_response(jsonify(resp), 200)

@api.route("/languages", methods=["GET"])
def get_languages():
    model = util.get_model()

    langs = model.Language.query.all()
    filter_langs = [x.get_output_dict() for x in langs if x.is_enabled]

    return make_response(jsonify(filter_langs), 200)

@api.route("/current-user", methods=["GET"])
@jwt_required
def get_current_user():
    model = util.get_model()

    current_user_id = get_jwt_identity()
    current_user = model.User.query.filter_by(id=current_user_id).scalar()

    resp = None
    if current_user:
        resp = current_user.get_output_dict()

    return make_response(jsonify(resp), 200)

@api.route("/submit-run", methods=["POST"])
@jwt_required
def submit_run():
    model = util.get_model()

    lang_name = request.json.get('lang', None)
    problem_slug = request.json.get('problem_slug', None)
    source_code = request.json.get('source_code', None)
    is_submission = request.json.get('is_submission', False)

    current_user_id = get_jwt_identity()
    user = model.User.query.filter_by(id=current_user_id).scalar()

    lang = model.Language.query.filter_by(name=lang_name).one()
    problem = model.Problem.query.filter_by(slug=problem_slug).scalar()
    contest = model.Contest.query.first()

    if is_submission:
        run_input = problem.secret_input
        run_output = problem.secret_output
    else:
        run_input = problem.sample_input
        run_output = problem.sample_output

    run = model.Run(user, contest,
                    lang, problem, datetime.datetime.utcnow(), source_code,
                    run_input, run_output, is_submission)

    model.db.session.add(run)
    model.db.session.commit()

    return "good"


def clean_output_string(s):
    """Cleans up an output string for comparison"""
    return s.replace("\r\n", "\n").strip()

@api.route("/", methods=["GET"])
def index():
    return abort(404)
