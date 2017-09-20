import os
import sys

sys.path.append(os.getcwd())

import subprocess

import web

bind = "0.0.0.0:9191"

workers = 8


def on_starting(_):
    web.setup_database(web.app)
    # subprocess.Popen(["python", "event_loop.py"])
