#!/usr/bin/env /bin/bash

set -o errexit

if python3 -m pipenv --venv > /dev/null 2>&1; then
    PYTHON=`python3 -m pipenv --py 2> /dev/null`
    echo "Python interpreter:" ${PYTHON}
else
	echo "Virtual environment not found."
	exit 1
fi

echo "🔤 isort formatting..."
python3 -m isort src tests

echo "🎨 autopep8 formatting..."
python3 -m autopep8 --in-place --recursive src tests

echo "🎉 formatted 🎉"
