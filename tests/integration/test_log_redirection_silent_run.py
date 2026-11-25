"""End-to-end test of an Actor redirecting the log of another Actor that stays silent for six minutes."""

from __future__ import annotations

import base64
import re
import subprocess
from datetime import timedelta
from pathlib import Path

from .._utils import create_built_actor, get_api_url, get_random_resource_name
from apify_client import ApifyClient
from apify_client._models import Run

REPO_ROOT = Path(__file__).resolve().parents[2]

LOGGED_UNTIL_S = 30
SILENT_UNTIL_S = 390
COUNT_UNTIL_S = 420

SILENT_ACTOR_SOURCE_FILES = [
    {
        'name': 'Dockerfile',
        'format': 'TEXT',
        'content': 'FROM apify/actor-node:26\nCOPY . ./\nCMD ["node", "main.mjs"]\n',
    },
    {
        'name': 'main.mjs',
        'format': 'TEXT',
        'content': f"""
for (let second = 0; second < {COUNT_UNTIL_S}; second++) {{
    if (second < {LOGGED_UNTIL_S} || second >= {SILENT_UNTIL_S}) {{
        console.log(`COUNTER-${{String(second).padStart(3, '0')}}`);
    }}
    await new Promise((resolve) => setTimeout(resolve, 1000));
}}
await new Promise((resolve) => setTimeout(resolve, 5000));
""",
    },
]
"""Source of an Actor that counts seconds: it logs the count for the first `LOGGED_UNTIL_S` seconds, counts silently
until `SILENT_UNTIL_S`, and then logs the count again until `COUNT_UNTIL_S`."""

REDIRECTOR_MAIN = """
import os
from unittest.mock import create_autospec

from apify_client import ApifyClient
from apify_client._resource_clients import LogClient

# Counts how many times the log stream is opened, to show the platform closed it during the silence.
stream = create_autospec(LogClient.stream, side_effect=LogClient.stream)
LogClient.stream = stream

client = ApifyClient(os.environ['APIFY_TOKEN'], api_url=os.environ['APIFY_API_BASE_URL'])
store = client.key_value_store(os.environ['ACTOR_DEFAULT_KEY_VALUE_STORE_ID'])
target_actor_id = store.get_record('INPUT')['value']['targetActorId']

# The default logger redirects the target run's log into this run's log.
run = client.actor(target_actor_id).call(memory_mbytes=256)

print(f'REDIRECTOR: target run finished as {run.status}', flush=True)
print(f'REDIRECTOR: log stream opened {stream.call_count} times', flush=True)
"""
"""Source of an Actor that calls the target Actor and redirects its log into its own log."""


def build_client_wheel(out_dir: Path) -> Path:
    """Build a wheel of the client in this checkout, so the redirecting Actor runs the code under test."""
    subprocess.run(  # noqa: S603
        ['uv', 'build', '--wheel', '--out-dir', str(out_dir)],  # noqa: S607
        check=True,
        capture_output=True,
        cwd=REPO_ROOT,
    )
    return next(out_dir.glob('apify_client-*.whl'))


def get_redirector_source_files(wheel: Path) -> list[dict[str, str]]:
    return [
        {
            'name': 'Dockerfile',
            'format': 'TEXT',
            'content': (
                'FROM apify/actor-python:3.13\n'
                'COPY . ./\n'
                f'RUN pip install --no-cache-dir ./{wheel.name}\n'
                'CMD ["python", "-u", "main.py"]\n'
            ),
        },
        {'name': 'main.py', 'format': 'TEXT', 'content': REDIRECTOR_MAIN},
        {'name': wheel.name, 'format': 'BASE64', 'content': base64.b64encode(wheel.read_bytes()).decode()},
    ]


def test_actor_redirects_log_of_actor_silent_for_six_minutes(api_token: str, tmp_path: Path) -> None:
    """An Actor redirects every line of another Actor's run exactly once, although that run stays silent for six
    minutes and the platform closes the log stream meanwhile."""
    client = ApifyClient(api_token, api_url=get_api_url())
    wheel = build_client_wheel(tmp_path)

    with (
        create_built_actor(client, get_random_resource_name('silent'), SILENT_ACTOR_SOURCE_FILES) as target_actor_id,
        # Full permissions, so the run token can start the target Actor and read its log.
        create_built_actor(
            client,
            get_random_resource_name('redirector'),
            get_redirector_source_files(wheel),
            actor_permission_level='FULL_PERMISSIONS',
        ) as redirector_actor_id,
    ):
        redirector_run = client.actor(redirector_actor_id).call(
            run_input={'targetActorId': target_actor_id},
            memory_mbytes=256,
            run_timeout=timedelta(minutes=15),
            logger=None,
        )
        assert isinstance(redirector_run, Run)
        redirector_log = client.run(redirector_run.id).log().get()
        assert redirector_log is not None
        assert redirector_run.status == 'SUCCEEDED', redirector_log

    assert 'REDIRECTOR: target run finished as SUCCEEDED' in redirector_log, redirector_log
    counted_seconds = [*range(LOGGED_UNTIL_S), *range(SILENT_UNTIL_S, COUNT_UNTIL_S)]
    expected_lines = [f'COUNTER-{second:03d}' for second in counted_seconds]
    assert re.findall(r'COUNTER-\d{3}', redirector_log) == expected_lines, redirector_log
    # The platform closed the stream during the silence, so the lines after it came over a reopened stream.
    stream_opens = re.search(r'REDIRECTOR: log stream opened (\d+) times', redirector_log)
    assert stream_opens is not None, redirector_log
    assert int(stream_opens[1]) >= 2, redirector_log
