#!/usr/bin/bash

# dev
tag="0.0.0."`date '+%s'`
git tag $tag
conda env remove -n deploy
conda create -n deploy python==3.8 -y
conda activate deploy
pip install build
pip install setuptools_scm
python -m build
git tag -d $tag
twine check dist/*
twine upload dist/*
pip install -e .[deploy]
cd GitHubHealth/app
pip freeze > requirements2.txt
diff requirements.txt requirements2.txt
mv requirements2.txt requirements.txt
conda deactivate
cd -

# check everything has gone ok up until now
# the version in requirements.txt should match the tag just created
# then do the following:

# test locally:
# python -m GitHubHealth.app.main

# deploy "app" for dev or "run" for prd
# follow prompts and check url
# gcloud [app|run] deploy

# TODOs:
# automated timestamp tag for dev and user specified version for prod
# figure out DNS settings for different versions of the deployed app
# including aliases, CNAMES etc.
# how to use the app.yaml file properly
