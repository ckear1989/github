#!/usr/bin/bash


# if you use conda try to manage your environment before running
# conda env remove -n GitHubHealth
# conda create -n GitHubHealth python==3.8 -y
# conda activate GitHubHealth
# pip install -e .[dev,test]

python3 -m GitHubHealth.app.main
