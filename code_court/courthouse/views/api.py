"""
Contains api endpoints for the defendant frontend
and external services
"""
import datetime
import json
import re

import six

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
@executioner_auth.get_password
def get_pw(email):
    model = get_model()
    user = model.User.query.filter_by(email=email).first()
    if user is not None and "executioner" in [x.id for x in user.user_roles]:
        return user.password
    return None

@executioner_auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)

# api routes
@api.route("/get-writ", methods=["GET"])
@executioner_auth.login_required
def get_writ():
    """endpoint for executioners to get runs to execute"""
    model = get_model()
    chosen_run = model.Run.query.filter_by(started_execing_time=None)\
                                          .order_by(model.Run.submit_time.desc()).first()
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
    model = get_model()
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
    model.db.session.commit()

    # TODO: perform judging
    return "Good"

@api.route("/", methods=["GET"])
def index():
    return abort(404)

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
