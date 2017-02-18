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

def clean_output_string(s):
    """Cleans up an output string for comparison"""
    return s.replace("\r\n", "\n").strip()

@api.route("/", methods=["GET"])
def index():
    return abort(404)
