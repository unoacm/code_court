import json
import re

from flask import (
    abort,
    Blueprint,
    current_app,
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
    current_app.logger.info("Test log")
    return render_template("admin_index.html")

@admin.route("/users", methods=["GET"])
def users():
    """
    The index page for the admin interface, contains
    a list of links to other admin pages
    """
    return render_template("users.html")
