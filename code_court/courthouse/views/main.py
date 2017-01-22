from flask import Blueprint, render_template, send_from_directory
from util import *

main = Blueprint('main', __name__,
                        template_folder='templates')

@main.route('/')
def index():
    return render_template("index.html")

@main.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)
