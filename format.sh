#!/usr/bin/env /bin/bash

set -o errexit

echo "🔤 isort formatting..."
python3 -m isort src tests

echo "🎨 autopep8 formatting..."
python3 -m autopep8 --in-place --recursive src tests

echo "🎉 formatted 🎉"
