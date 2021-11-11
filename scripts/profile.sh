#!/usr/bin/bash

python -m cProfile -s tottime scripts/profile.py > profile.log
