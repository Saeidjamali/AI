#!/bin/bash
source /opt/anaconda/etc/profile.d/conda.sh
conda activate rasa_3
rasa run --enable-api --cors "*" --debug
