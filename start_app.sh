#!/bin/bash

. .venv/bin/activate
export FLASK_APP=yclins.py
export FLAST_ENV=development


flask db migrate
flask db upgrade

flask run --host=:: --port=5000



