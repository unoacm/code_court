"""
Contains routes for handling authentication
"""
import util

from flask_login import login_user, logout_user
from sqlalchemy.orm.exc import NoResultFound

from flask import (
    abort,
    Blueprint,
    redirect,
    render_template,
    request,
    flash,
)

auth = Blueprint('auth', __name__,
                template_folder='templates')

@auth.route("/login", methods=["GET"])
@util.ssl_required
def login_view():
    """general login page"""
    return render_template("auth/login.html")

@auth.route("/login", methods=["POST"])
@util.ssl_required
def login_submit():
    """processes login requests"""
    model = util.get_model()

    if "email" not in request.form:
        flash("Email not found", "danger")
        abort(401)

    if "password" not in request.form:
        flash("Password not found", "danger")
        abort(401)

    email = request.form.get("email")
    password = request.form.get("password")

    try:
        user = model.User.query.filter_by(email=email).one()
    except NoResultFound as e:
        flash("Invalid username or password", "danger")
        abort(401)

    is_matching = user.verify_password(password)
    if is_matching:
        flash("Login successful", "success")
        login_user(user)
        return redirect("/admin")
    else:
        flash("Invalid username or password", "danger")
        abort(401)

@auth.route("/profile", methods=["GET"])
def profile():
    return render_template("auth/profile.html")

@auth.route("/logout", methods=["GET"])
def logout_submit():
    """processes logout requests"""
    logout_user()
    return redirect("/admin")
