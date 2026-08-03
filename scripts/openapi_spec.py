"""Fetch the published OpenAPI specification and record the version the models were generated from.

`poe generate-models` runs `fetch` first and both codegen passes read the downloaded file, so a specification
redeployed mid-run cannot produce models built from two different inputs. The download lands in `tmp/`, which is
not committed - the repository stores only the specification *version*, in `[tool.apify.openapi-spec]` in
`pyproject.toml`.

`record-version` writes that version and runs last, after generation succeeded, so the recorded version always
names the specification the committed `_models.py`, `_typeddicts.py`, and `_literals.py` actually follow from. It
is provenance, not a codegen input: the published specification is served latest-only, so the version cannot be
used to fetch that exact document back.

`recorded-version` prints the currently recorded version without touching anything. The nightly regeneration
workflow reads it before regenerating, so its pull request can say whether the specification moved at all - a
model diff with an unchanged version comes from the codegen tooling, not from the API.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import tomllib
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
VERSION_TABLE_PATH = ('tool', 'apify', 'openapi-spec')
VERSION_TABLE = f'[{".".join(VERSION_TABLE_PATH)}]'
VERSION_KEY = 'version'

# Reading goes through `tomllib`, but writing has to preserve the surrounding comments, so the value is replaced
# in place. Both patterns tolerate the whitespace and trailing comments TOML allows, so reformatting
# `pyproject.toml` cannot quietly break the nightly regeneration.
TABLE_HEADER_PATTERN = re.compile(rf'^\s*\[\s*{re.escape(".".join(VERSION_TABLE_PATH))}\s*\]\s*(?:#.*)?$')
ANY_TABLE_HEADER_PATTERN = re.compile(r'^\s*\[')
VERSION_ENTRY_PATTERN = re.compile(rf'^(?P<prefix>\s*{VERSION_KEY}\s*=\s*)"(?P<value>[^"]*)"(?P<suffix>.*)$')

# A truncated response or an error page must never be generated from. The real specification is roughly 1 MB, so
# a response anywhere near this floor is broken rather than merely small.
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

    if not isinstance(spec, dict):
        fail(f'Downloaded specification is a JSON {type(spec).__name__}, not an object - aborting.')

    missing_keys = [key for key in REQUIRED_SPEC_KEYS if key not in spec]
    if missing_keys:
        fail(f'Downloaded specification is missing top-level {", ".join(missing_keys)} - aborting.')

    info = spec['info']
    version = info.get(VERSION_KEY) if isinstance(info, dict) else None
    if not isinstance(version, str) or not version:
        fail('Downloaded specification has no `info.version` string - aborting.')

    return version


def fetch() -> None:
    """Download the published specification for codegen to read."""
    payload = download_spec()
    version = read_spec_version(payload)

    # Written byte for byte, so the key order the generator sees is the published one: `keep_model_order` ties
    # the order of the generated models to it.
    SPEC_PATH.parent.mkdir(parents=True, exist_ok=True)
    SPEC_PATH.write_bytes(payload)

    print(f'Wrote {SPEC_PATH.relative_to(REPO_ROOT)} (version {version}, {len(payload)} bytes).')


def read_recorded_version() -> str:
    """Return the specification version currently recorded in `pyproject.toml`."""
    try:
        config = tomllib.loads(PYPROJECT_PATH.read_text(encoding='utf-8'))
    except tomllib.TOMLDecodeError as exc:
        fail(f'{PYPROJECT_PATH.name} is not valid TOML: {exc}.')

    for key in VERSION_TABLE_PATH:
        if not isinstance(config, dict) or key not in config:
            fail(f'{PYPROJECT_PATH.name} has no {VERSION_TABLE} table - cannot read the specification version.')
        config = config[key]

    version = config.get(VERSION_KEY) if isinstance(config, dict) else None
    if not isinstance(version, str) or not version:
        fail(f'{VERSION_TABLE} in {PYPROJECT_PATH.name} has no `{VERSION_KEY}` string.')

    return version


def write_recorded_version(version: str) -> None:
    """Replace the recorded specification version in `pyproject.toml`, leaving the rest of the file untouched."""
    lines = PYPROJECT_PATH.read_text(encoding='utf-8').splitlines(keepends=True)

    try:
        table_index = next(index for index, line in enumerate(lines) if TABLE_HEADER_PATTERN.match(line.rstrip('\n')))
    except StopIteration:
        fail(f'{PYPROJECT_PATH.name} has no {VERSION_TABLE} table - cannot record the specification version.')

    # Only the table's own entries may be rewritten, so a missing key can't silently hit the next table's `version`.
    for index in range(table_index + 1, len(lines)):
        line = lines[index].rstrip('\n')
        if ANY_TABLE_HEADER_PATTERN.match(line):
            break

        match = VERSION_ENTRY_PATTERN.match(line)
        if match:
            lines[index] = f'{match["prefix"]}"{version}"{match["suffix"]}\n'
            PYPROJECT_PATH.write_text(''.join(lines), encoding='utf-8', newline='\n')
            return

    fail(f'{VERSION_TABLE} in {PYPROJECT_PATH.name} has no `{VERSION_KEY}` entry - cannot record the version.')


def record_version() -> None:
    """Record the fetched specification's version in `pyproject.toml`."""
    if not SPEC_PATH.is_file():
        fail(f'{SPEC_PATH.relative_to(REPO_ROOT)} is missing - run `poe generate-models` instead of this alone.')

    version = read_spec_version(SPEC_PATH.read_bytes())
    previous = read_recorded_version()

    if previous == version:
        print(f'Specification version {version} is already recorded in {PYPROJECT_PATH.name}.')
        return

    write_recorded_version(version)
    print(f'Recorded specification version in {PYPROJECT_PATH.name}: {previous} -> {version}.')


def recorded_version() -> None:
    """Print the recorded specification version, for the regeneration workflow to read."""
    print(read_recorded_version())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(required=True)

    fetch_parser = subparsers.add_parser('fetch', help='download the published specification into tmp/')
    fetch_parser.set_defaults(handler=fetch)

    record_parser = subparsers.add_parser(
        'record-version', help="record the fetched specification's version in pyproject.toml"
    )
    record_parser.set_defaults(handler=record_version)

    show_parser = subparsers.add_parser(
        'recorded-version', help='print the specification version recorded in pyproject.toml'
    )
    show_parser.set_defaults(handler=recorded_version)

    parser.parse_args().handler()


if __name__ == '__main__':
    main()
