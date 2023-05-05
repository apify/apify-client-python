# Apify API client for Python

The Apify API Client for Python is the official library to access the [Apify API](https://docs.apify.com/api/v2) from your Python applications.
It provides useful features like automatic retries and convenience functions to improve your experience with the Apify API.

If you want to develop Apify Actors in Python,
check out the [Apify SDK for Python](https://docs.apify.com/sdk/python) instead.

## Installation

Requires Python 3.8+

You can install the package from its [PyPI listing](https://pypi.org/project/apify-client).
To do that, simply run `pip install apify-client` in your terminal.

## Usage

For usage instructions, check the documentation on [Apify Docs](https://docs.apify.com/api/client/python/) or in [`docs/docs.md`](docs/docs.md).

## Development

### Environment

For local development, it is required to have Python 3.8 installed.

It is recommended to set up a virtual environment while developing this package to isolate your development environment,
however, due to the many varied ways Python can be installed and virtual environments can be set up,
this is left up to the developers to do themselves.

One recommended way is with the built-in `venv` module:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

To improve on the experience, you can use [pyenv](https://github.com/pyenv/pyenv) to have an environment with a pinned Python version,
and [direnv](https://github.com/direnv/direnv) to automatically activate/deactivate the environment when you enter/exit the project folder.

### Dependencies

To install this package and its development dependencies, run `make install-dev`

### Formatting

We use `autopep8` and `isort` to automatically format the code to a common format. To run the formatting, just run `make format`.

### Linting, type-checking and unit testing

We use `flake8` for linting, `mypy` for type checking and `pytest` for unit testing. To run these tools, just run `make check-code`.

### Documentation

We use the [Google docstring format](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html) for documenting the code.
We document every user-facing class or method, and enforce that using the flake8-docstrings library.

The documentation is then rendered from the docstrings in the code using Sphinx and some heavy post-processing and saved as `docs/docs.md`.
To generate the documentation, just run `make docs`.

### Release process

Publishing new versions to [PyPI](https://pypi.org/project/apify-client) happens automatically through GitHub Actions.

On each commit to the `master` branch, a new beta release is published, taking the version number from `pyproject.toml`
and automatically incrementing the beta version suffix by 1 from the last beta release published to PyPI.

A stable version is published when a new release is created using GitHub Releases, again taking the version number from `pyproject.toml`. The built package assets are automatically uploaded to the GitHub release.

If there is already a stable version with the same version number as in `pyproject.toml` published to PyPI, the publish process fails,
so don't forget to update the version number before releasing a new version.
The release process also fails when the released version is not described in `CHANGELOG.md`,
so don't forget to describe the changes in the new version there.
