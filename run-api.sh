#!/bin/bash
PORT=500"${HOSTNAME: -1}"
FLASK_APP=api.py flask run --host=0.0.0.0 --port=$PORT