#!/bin/bash
gunicorn web:app -c gunicorn_config.py