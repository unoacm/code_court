import subprocess

bind = "0.0.0.0:9191"

def on_starting(_):
    subprocess.Popen(["python", "event_loop.py"])
