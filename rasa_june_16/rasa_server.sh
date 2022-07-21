#!/bin/sh
CONDA_VERSION="rasa_3"
conda activate $CONDA_VERSION
rasa run actions
