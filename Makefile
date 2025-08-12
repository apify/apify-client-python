.PHONY: clean install-dev build publish-to-pypi lint type-check unit-tests unit-tests-cov \
        integration-tests format check-async-docstrings check-code fix-async-docstrings \
        build-api-reference build-docs run-docs

# This is default for local testing, but GitHub workflows override it to a higher value in CI
INTEGRATION_TESTS_CONCURRENCY = 1

clean:
	rm -rf .mypy_cache .pytest_cache .ruff_cache build dist htmlcov .coverage

install-dev:
	uv sync --all-extras
	uv run pre-commit install

build:
	uv build --verbose

# APIFY_PYPI_TOKEN_CRAWLEE is expected to be set in the environment
publish-to-pypi:
	uv publish --verbose --token "${APIFY_PYPI_TOKEN_CRAWLEE}"

lint:
	uv run ruff format --check
	uv run ruff check

type-check:
	uv run mypy

unit-tests:
	uv run pytest --numprocesses=auto --verbose --cov=src/apify_client tests/unit

unit-tests-cov:
	uv run pytest --numprocesses=auto --verbose --cov=src/apify_client --cov-report=html tests/unit

integration-tests:
	uv run pytest --numprocesses=$(INTEGRATION_TESTS_CONCURRENCY) --verbose tests/integration

format:
	uv run ruff check --fix
	uv run ruff format

check-async-docstrings:
	uv run python scripts/check_async_docstrings.py

# The check-code target runs a series of checks equivalent to those performed by pre-commit hooks
# and the run_checks.yaml GitHub Actions workflow.
check-code: lint type-check unit-tests check-async-docstrings

fix-async-docstrings:
	uv run python scripts/fix_async_docstrings.py

build-api-reference:
	cd website && uv run ./build_api_reference.sh

build-docs:
	cd website && uv run npm clean-install && uv run npm run build

run-docs: build-api-reference
	cd website && uv run npm clean-install && uv run npm run start
