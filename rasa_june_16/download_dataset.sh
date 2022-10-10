#!/bin/bash

source /opt/chatbot/.env
aws s3 cp --quiet s3://ithing-$ENV-data/viki_userdata/updated_fitbit_dataset.csv /opt/chatbot/updated_fitbit_dataset.csv || true
