.PHONY: clean install-dev lint unit-tests type-check check-code format check-async-docstrings fix-async-docstrings check-changelog-entry build-api-reference

clean:
	rm -rf build dist .mypy_cache .pytest_cache src/*.egg-info __pycache__

install-dev:
	python -m pip install --upgrade pip
	pip install --upgrade setuptools wheel
	pip install --no-cache-dir -e ".[dev]"
	pre-commit install

lint:
	python3 -m flake8

unit-tests:
	python3 -m pytest -n auto -ra tests/unit

type-check:
	python3 -m mypy

check-code: lint check-async-docstrings type-check unit-tests

format:
	python3 -m isort src tests
	python3 -m autopep8 --in-place --recursive src tests

check-async-docstrings:
	python3 scripts/check_async_docstrings.py

fix-async-docstrings:
	python3 scripts/fix_async_docstrings.py

check-changelog-entry:
	python3 scripts/check_version_in_changelog.py

build-api-reference:
	pydoc-markdown --quiet --dump > website/docspec-dump.json
	cd website && node transformDocs.js ./docspec-dump.json
