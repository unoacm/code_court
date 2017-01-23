"""
Contains api endpoints for the defendant frontend
and external services
"""
import json
import re

from flask import (
    abort,
    Blueprint,
    current_app,
    render_template,
)

api = Blueprint('api', __name__,
                template_folder='templates')

@api.route("/", methods=["GET"])
def index():
    return abort(404)
