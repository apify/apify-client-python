.PHONY: lint test type-check check-all format docs

lint:
	python3 -m flake8 src tests

test:
	python3 -m pytest -rA --doctest-modules src tests

type-check:
	python3 -m mypy src

check-all: lint type-check test

format:
	python3 -m isort src tests
	python3 -m autopep8 --in-place --recursive src tests

docs:
	# Sphinx is pretty chatty, so we silence it this way
	./docs/res/build.sh > /dev/null
