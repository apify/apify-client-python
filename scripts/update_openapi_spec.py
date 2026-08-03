"""Sync the committed OpenAPI specification snapshot with the published one.

The snapshot in `spec/openapi.json` is the single input the models are generated from, so codegen output is a
function of committed state alone: the same snapshot plus the same pinned tooling always produces the same
`_models.py`, `_typeddicts.py`, and `_literals.py`. That is what lets `poe check-models` verify the generated
files in CI without reaching for the network.

Run this (via `poe update-spec`) to pull in the latest published specification, then regenerate the models with
`poe generate-models`.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import impit

REPO_ROOT = Path(__file__).resolve().parent.parent

# The published, bundled specification. It is built and deployed from the `apify/apify-docs` repository.
SPEC_URL = 'https://docs.apify.com/api/openapi.json'

SPEC_PATH = REPO_ROOT / 'spec' / 'openapi.json'

# A truncated response or an error page must never overwrite the snapshot. The real specification is roughly
# 1 MB, so anything remotely this small is broken.
MIN_SPEC_SIZE_BYTES = 100_000

# Top-level members every specification we can generate models from has to contain. `info` is included because
# the version stamp reported below is read from it.
REQUIRED_SPEC_KEYS = ('openapi', 'info', 'paths', 'components')

REQUEST_TIMEOUT_SECS = 60

# The nightly workflow alerts the team when this fails, so a single network blip shouldn't be worth a ping.
DOWNLOAD_ATTEMPTS = 3
RETRY_DELAY_SECS = 5


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

    print(f'Failed to download {SPEC_URL} after {DOWNLOAD_ATTEMPTS} attempts: {last_error}.', file=sys.stderr)
    sys.exit(1)


def main() -> None:
    payload = download_spec()

    if len(payload) < MIN_SPEC_SIZE_BYTES:
        print(
            f'Downloaded specification is only {len(payload)} bytes, which cannot be the real one - aborting.',
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        spec = json.loads(payload)
    except json.JSONDecodeError as exc:
        print(f'Downloaded specification is not valid JSON: {exc}.', file=sys.stderr)
        sys.exit(1)

    missing_keys = [key for key in REQUIRED_SPEC_KEYS if key not in spec]
    if missing_keys:
        print(f'Downloaded specification is missing top-level {", ".join(missing_keys)} - aborting.', file=sys.stderr)
        sys.exit(1)

    # Read the version stamp before writing anything, so a malformed `info` aborts with the snapshot intact.
    version = spec['info'].get('version')
    if not version:
        print('Downloaded specification has no `info.version` - aborting.', file=sys.stderr)
        sys.exit(1)

    # Normalize the formatting so the committed diffs stay readable no matter how the published bundle is
    # formatted. Key order is deliberately preserved: `keep_model_order` makes the generated model order follow
    # the specification, so sorting keys here would reshuffle `_models.py` on the next run.
    normalized = json.dumps(spec, indent=2, ensure_ascii=False) + '\n'

    SPEC_PATH.parent.mkdir(parents=True, exist_ok=True)
    SPEC_PATH.write_text(normalized, encoding='utf-8', newline='\n')

    print(f'Wrote {SPEC_PATH.relative_to(REPO_ROOT)} (version {version}, {len(normalized.encode())} bytes).')


if __name__ == '__main__':
    main()
