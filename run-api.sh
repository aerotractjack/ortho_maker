#!/bin/bash
PORT=500"${HOSTNAME: -1}"
FLASK_APP=api.py /home/aerotract/.local/bin/flask run --host=0.0.0.0 --port=$PORT