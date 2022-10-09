#!/bin/bash

# output to syslog
exec 1> >(logger -s -t $(basename $0)) 2>&1

source /opt/rasa_venv/bin/activate
cd /opt/chatbot
python database_to_csv.py
