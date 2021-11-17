#!/usr/bin/bash

# conda env remove -n GitHubHealth
# conda create -n GitHubHealth python==3.8 -y

conda activate GitHubHealth
python -m app.main
conda deactivate
