import json
import re

from flask import (
    Blueprint,
    render_template,
)

admin = Blueprint('admin', __name__,
                  template_folder='templates')

@admin.route("/", methods=["GET"])
def index():
    """
    The index page for the admin interface, contains
    a list of links to other admin pages
    """
    return render_template("admin_index.html")
