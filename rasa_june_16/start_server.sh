#!/bin/bash
source /opt/rasa_venv/bin/activate
rasa run --enable-api --cors "*" --debug
