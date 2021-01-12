# Apify API client for Python

This will be an official client for [Apify API](https://www.apify.com/docs/api/v2).
It's still work in progress, so please don't use it yet!

TODO: write a proper README

## Installation

Requires Python 3.7+

TODO: describe `pip install apify_client`, link to PyPI

## Development

### Environment

For local development, it is required to have Python 3.7 installed.

It is recommended to set up a virtual environment while developing this package to isolate your development environment,
however, due to the many varied ways Python can be installed and virtual environments can be set up,
this is left up to the developers to do themselves.

One recommended way is with the builtin `venv` module:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

To improve on the experience, you can use [pyenv](https://github.com/pyenv/pyenv) to have an environment with a pinned Python version,
and [direnv](https://github.com/direnv/direnv) to automatically activate/deactivate the environment when you enter/exit the project folder.

### Dependencies

To install this package and its development dependencies, run `pip install -e '.[dev]'`

### Formatting

We use `autopep8` and `isort` to automatically format the code to a common format. To run the formatting, just run `./format.sh`.

### Linting and Testing

We use `flake8` for linting, `mypy` for type checking and `pytest` for unit testing. To run these tools, just run `./lint_and_test.sh`.
