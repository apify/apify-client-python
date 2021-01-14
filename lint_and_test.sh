#!/usr/bin/env bash

set -ue

checks_to_run=${1:-"everything"}
shift || true


lint() {
    echo "⛄️ flake8 check..."
    python3 -m flake8 src tests
}

type_check() {
    echo "📝 checking types"
    python3 -m mypy src
}

unit_tests() {
    echo "👮‍♀️ running unit tests"
    python3 -m pytest -rA tests
}


if [ "$checks_to_run" = "lint" ] ; then
    lint
elif [ "$checks_to_run" = "types" ] ; then
    type_check
elif [ "$checks_to_run" = "tests" ] ; then
    unit_tests
elif [ "$checks_to_run" = "everything" ] ; then
    lint
    type_check
    unit_tests
else
    echo "Invalid type of test ($checks_to_run) requested. Use lint / types / tests or leave empty to run all tests"
    exit 1
fi

echo "🎉 success 🎉"
