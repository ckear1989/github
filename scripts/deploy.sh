#!/usr/bin/bash

tag=$1
git tag $tag
git push --tags
conda env remove -n deploy
conda create -n deploy python==3.8 -y
conda activate deploy
pip install build
pip install setuptools_scm
python -m build
pip install .
# pip freeze > app/requirements.txt
# twine check dist/GitHubHealth*${tag}*
# twine upload dist/GitHubHealth*${tag}*
# cd app && gcloud app deploy && cd -
# conda deactivate
