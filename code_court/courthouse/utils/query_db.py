#!/usr/bin/env python

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import IPython

from flask import Flask

import model
from model import db

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/code_court.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['model'] = model

db.init_app(app)

with app.app_context():
    IPython.embed()
