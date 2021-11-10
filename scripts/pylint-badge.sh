#!/usr/bin/bash

pylint --output=pylint.txt --output-format=text $1
score=$(sed -n 's/^Your code has been rated at \([-0-9.]*\)\/.*/\1/p' pylint.txt)
echo "Pylint score was $score"
anybadge --value=$score --file=data/pylint.svg -o pylint
