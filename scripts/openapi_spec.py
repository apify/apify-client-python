"""Fetch the published OpenAPI specification and record the version the models were generated from.

`poe generate-models` runs `fetch` first and both codegen passes read the downloaded file, so a specification
redeployed mid-run cannot produce models built from two different inputs. The download lands in `tmp/`, which is
not committed - the repository stores only the specification *version*, in `[tool.apify.openapi-spec]` in
`pyproject.toml`.

`record-version` writes that version and runs last, after generation succeeded, so the recorded version always
names the specification the committed `_models.py`, `_typeddicts.py`, and `_literals.py` actually follow from. It
is provenance, not a codegen input: the published specification is served latest-only, so the version cannot be
used to fetch that exact document back.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import NoReturn

import impit

REPO_ROOT = Path(__file__).resolve().parent.parent

# The published, bundled specification. It is built and deployed from the `apify/apify-docs` repository.
SPEC_URL = 'https://docs.apify.com/api/openapi.json'

# Codegen input, deliberately outside version control - `tmp/` is git-ignored.
SPEC_PATH = REPO_ROOT / 'tmp' / 'openapi.json'

PYPROJECT_PATH = REPO_ROOT / 'pyproject.toml'

# The table holding the recorded specification version, and the key within it.
VERSION_TABLE = '[tool.apify.openapi-spec]'
VERSION_KEY = 'version'

# A truncated response or an error page must never be generated from. The real specification is roughly 1 MB, so
# anything remotely this small is broken.
MIN_SPEC_SIZE_BYTES = 100_000

# Top-level members every specification we can generate models from has to contain. `info` is included because
# the recorded version is read from it.
REQUIRED_SPEC_KEYS = ('openapi', 'info', 'paths', 'components')

REQUEST_TIMEOUT_SECS = 60

# The nightly workflow alerts the team when this fails, so a single network blip shouldn't be worth a ping.
DOWNLOAD_ATTEMPTS = 3
RETRY_DELAY_SECS = 5


def fail(message: str) -> NoReturn:
    """Report a failure on stderr and exit non-zero."""
    print(message, file=sys.stderr)
    sys.exit(1)


def download_spec() -> bytes:
    """Download the published specification, retrying transient failures."""
    last_error = ''

    with impit.Client(follow_redirects=True) as client:
        for attempt in range(1, DOWNLOAD_ATTEMPTS + 1):
            try:
                response = client.request('GET', SPEC_URL, timeout=REQUEST_TIMEOUT_SECS)
            except Exception as exc:
                last_error = f'{type(exc).__name__}: {exc}'
            else:
                if response.status_code == 200:
                    return response.content
                last_error = f'HTTP {response.status_code}'

            print(f'Attempt {attempt}/{DOWNLOAD_ATTEMPTS} to download {SPEC_URL} failed ({last_error}).')
            if attempt < DOWNLOAD_ATTEMPTS:
                time.sleep(RETRY_DELAY_SECS)

    fail(f'Failed to download {SPEC_URL} after {DOWNLOAD_ATTEMPTS} attempts: {last_error}.')


def read_spec_version(payload: bytes) -> str:
    """Validate a downloaded specification and return its `info.version`."""
    if len(payload) < MIN_SPEC_SIZE_BYTES:
        fail(f'Downloaded specification is only {len(payload)} bytes, which cannot be the real one - aborting.')

    try:
        spec = json.loads(payload)
    except json.JSONDecodeError as exc:
        fail(f'Downloaded specification is not valid JSON: {exc}.')

    missing_keys = [key for key in REQUIRED_SPEC_KEYS if key not in spec]
    if missing_keys:
        fail(f'Downloaded specification is missing top-level {", ".join(missing_keys)} - aborting.')

    version = spec['info'].get(VERSION_KEY)
    if not version:
        fail('Downloaded specification has no `info.version` - aborting.')

    return str(version)


def fetch() -> None:
    """Download the published specification for codegen to read."""
    payload = download_spec()
    version = read_spec_version(payload)

    # Written byte for byte, so the key order the generator sees is the published one: `keep_model_order` ties
    # the order of the generated models to it.
    SPEC_PATH.parent.mkdir(parents=True, exist_ok=True)
    SPEC_PATH.write_bytes(payload)

    print(f'Wrote {SPEC_PATH.relative_to(REPO_ROOT)} (version {version}, {len(payload)} bytes).')


def record_version() -> None:
    """Record the fetched specification's version in `pyproject.toml`."""
    if not SPEC_PATH.is_file():
        fail(f'{SPEC_PATH.relative_to(REPO_ROOT)} is missing - run `poe generate-models` instead of this alone.')

    version = read_spec_version(SPEC_PATH.read_bytes())
    lines = PYPROJECT_PATH.read_text(encoding='utf-8').splitlines(keepends=True)

    try:
        table_index = next(index for index, line in enumerate(lines) if line.strip() == VERSION_TABLE)
    except StopIteration:
        fail(f'{PYPROJECT_PATH.name} has no {VERSION_TABLE} table - cannot record the specification version.')

    # Only the table's own keys may be rewritten, so a missing key can't silently hit the next table's `version`.
    for index in range(table_index + 1, len(lines)):
        line = lines[index]
        if line.lstrip().startswith('['):
            break
        if line.startswith(f'{VERSION_KEY} = '):
            previous = line.split('=', maxsplit=1)[1].strip().strip('"')
            if previous == version:
                print(f'Specification version {version} is already recorded in {PYPROJECT_PATH.name}.')
                return

            lines[index] = f'{VERSION_KEY} = "{version}"\n'
            PYPROJECT_PATH.write_text(''.join(lines), encoding='utf-8', newline='\n')
            print(f'Recorded specification version in {PYPROJECT_PATH.name}: {previous} -> {version}.')
            return

    fail(f'{VERSION_TABLE} in {PYPROJECT_PATH.name} has no `{VERSION_KEY}` key - cannot record the version.')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest='command', required=True)
    subparsers.add_parser('fetch', help='download the published specification into tmp/')
    subparsers.add_parser('record-version', help="record the fetched specification's version in pyproject.toml")

    if parser.parse_args().command == 'fetch':
        fetch()
    else:
        record_version()


if __name__ == '__main__':
    main()
