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
pip install .[deploy]
pip freeze > GitHubHealth/app/requirements2.txt
diff GitHubHealth/app/requirements.txt GitHubHealth/app/requirements2.txt
mv GitHubHealth/app/requirements2.txt GitHubHealth/app/requirements.txt
twine check dist/GitHubHealth*
twine upload dist/GitHubHealth*
cd GitHubHealth/app && gcloud app deploy && cd -
# cd GitHubHealth/app && gcloud run deploy && cd -
conda deactivate
