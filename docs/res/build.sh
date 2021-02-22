#!/usr/bin/env bash

cd "$( dirname "${BASH_SOURCE[0]}" )"

sphinx-build -M markdown sphinx-config build -a -E

mv build/markdown/index.md api_reference.md
rm -rf build

python format.py

cat intro.md api_reference.md > ../docs.md

rm api_reference.md
