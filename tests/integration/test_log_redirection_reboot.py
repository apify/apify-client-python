"""End-to-end test of resuming log redirection after the redirecting Actor reboots."""

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
TARGET_LINE_COUNT = 60
REBOOT_MARKER = 'REDIRECTOR: rebooting'

TARGET_SOURCE_FILES = [
    {
        'name': 'Dockerfile',
        'format': 'TEXT',
        'content': 'FROM apify/actor-node:26\nCOPY . ./\nCMD ["node", "main.mjs"]\n',
    },
    {
        'name': 'main.mjs',
        'format': 'TEXT',
        'content': f"""
for (let index = 0; index < {TARGET_LINE_COUNT}; index++) {{
    console.log(`TARGET-LINE-${{String(index).padStart(3, '0')}}`);
    await new Promise((resolve) => setTimeout(resolve, 1000));
}}
""",
    },
]
"""Source of an Actor that logs `TARGET_LINE_COUNT` numbered lines, one per second."""

REDIRECTOR_MAIN = f"""
import os
import time
from datetime import datetime, timedelta

from apify_client import ApifyClient

client = ApifyClient(os.environ['APIFY_TOKEN'], api_url=os.environ['APIFY_API_BASE_URL'])
store = client.key_value_store(os.environ['ACTOR_DEFAULT_KEY_VALUE_STORE_ID'])

state_record = store.get_record('STATE')
if state_record is None:
    target_actor_id = store.get_record('INPUT')['value']['targetActorId']
    target_run = client.actor(target_actor_id).start()
    state = {{'targetRunId': target_run.id, 'redirectedUntil': None}}
else:
    state = state_record['value']

run_client = client.run(state['targetRunId'])
since = None
if state['redirectedUntil']:
    since = datetime.fromisoformat(state['redirectedUntil']) + timedelta(milliseconds=1)
streamed_log = run_client.get_streamed_log(since=since)

if state_record is not None:
    # After the reboot: redirect the rest of the log. The stream of the finished run ends on its own, so let it,
    # instead of stopping it while it may still deliver the last lines.
    streaming_thread = streamed_log.start()
    run_client.wait_for_finish()
    streaming_thread.join(timeout=120)
    streamed_log.stop()
else:
    # Before the reboot: redirect a part of the log, save how far it got, and reboot.
    streamed_log.start()
    deadline = time.monotonic() + 300
    while streamed_log.last_redirected_at is None and time.monotonic() < deadline:
        time.sleep(1)
    time.sleep(15)
    streamed_log.stop()
    state['redirectedUntil'] = streamed_log.last_redirected_at.isoformat()
    store.set_record('STATE', state)
    print('{REBOOT_MARKER}', flush=True)
    client.run(os.environ['ACTOR_RUN_ID']).reboot()
    # The reboot replaces this container.
    time.sleep(600)
"""
"""Source of an Actor that redirects the log of a target Actor run, reboots midway, and resumes the redirection
from the `last_redirected_at` it saved in its key-value store."""


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


def test_streamed_log_resumes_after_redirecting_actor_reboots(api_token: str, tmp_path: Path) -> None:
    """Every line of the target run is redirected exactly once, across a reboot of the redirecting Actor."""
    client = ApifyClient(api_token, api_url=get_api_url())
    wheel = build_client_wheel(tmp_path)

    with (
        create_built_actor(client, get_random_resource_name('target'), TARGET_SOURCE_FILES) as target_actor_id,
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
            run_timeout=timedelta(minutes=10),
            logger=None,
        )
        assert isinstance(redirector_run, Run)
        redirector_log = client.run(redirector_run.id).log().get()
        assert redirector_run.status == 'SUCCEEDED', redirector_log
        assert redirector_log is not None

    assert redirector_log.count(REBOOT_MARKER) == 1, redirector_log
    before_reboot, after_reboot = redirector_log.split(REBOOT_MARKER)
    redirected_lines = re.findall(r'TARGET-LINE-\d{3}', redirector_log)
    expected_lines = [f'TARGET-LINE-{index:03d}' for index in range(TARGET_LINE_COUNT)]
    assert redirected_lines == expected_lines, redirector_log
    # The reboot happened midway, so both runs of the redirecting Actor redirected a part of the log.
    assert 'TARGET-LINE-' in before_reboot
    assert 'TARGET-LINE-' in after_reboot
