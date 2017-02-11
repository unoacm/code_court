import json
import re

import util

from flask import (
    Blueprint,
    render_template,
)

defendant = Blueprint('defendant', __name__,
                  template_folder='templates')

@defendant.route("/", methods=["GET"])
def index():
    """
    The index page for the defendant frontend
    """
    return render_template("defendant_index.html")
