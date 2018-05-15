from flask import Blueprint, send_from_directory

main = Blueprint("main", __name__, template_folder="templates")


@main.route("/flaskstatic/<path:path>")
def send_flask_static(path):
    return send_from_directory("static", path)
