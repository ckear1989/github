#!/usr/bin/bash

conda env remove -n deploy
conda create -n deploy python==3.8 -y
conda activate deploy
pip install build
pip install setuptools_scm
python -m build
pip install .
pip freeze > app/requirements.txt
cd app && gcloud app deploy
conda deactivate
