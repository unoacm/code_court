from flask import (
    current_app,
    Blueprint,
    render_template, )

import util

admin = Blueprint('admin', __name__, template_folder='templates')


@admin.route("/", methods=["GET"])
@util.login_required("operator")
def index():
    """
    The index page for the admin interface, contains
    a list of links to other admin pages
    """
    info = {
        "Database URI": current_app.config['SQLALCHEMY_DATABASE_URI'],
        "Run Mode": current_app.config['RUNMODE']
    }
    return render_template("admin_index.html", info=info)

