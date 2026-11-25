"""End-to-end test of log redirection from a run that stays silent for longer than the platform keeps a stream open."""

from __future__ import annotations

import logging
import re
from datetime import timedelta
from typing import TYPE_CHECKING
from unittest.mock import create_autospec

from .._utils import create_built_actor, get_api_url, get_random_resource_name
from apify_client import ApifyClient
from apify_client._models import Run
from apify_client._resource_clients import LogClient

if TYPE_CHECKING:
    import pytest
    from _pytest.logging import LogCaptureFixture

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


def test_streamed_log_resumes_after_platform_closes_silent_stream(
    api_token: str, caplog: LogCaptureFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Every line of a run that stays silent for six minutes is redirected exactly once, over a reopened stream."""
    client = ApifyClient(api_token, api_url=get_api_url())
    stream = create_autospec(LogClient.stream, side_effect=LogClient.stream)
    monkeypatch.setattr(LogClient, 'stream', stream)
    logger = logging.getLogger('apify_client.tests.silent_run')

    with (
        create_built_actor(client, get_random_resource_name('silent'), SILENT_ACTOR_SOURCE_FILES) as actor_id,
        caplog.at_level(logging.INFO, logger=logger.name),
    ):
        run = client.actor(actor_id).call(memory_mbytes=256, run_timeout=timedelta(minutes=10), logger=logger)
        assert isinstance(run, Run)
        assert run.status == 'SUCCEEDED'

    redirected = '\n'.join(record.message for record in caplog.records if record.name == logger.name)
    counted_seconds = [*range(LOGGED_UNTIL_S), *range(SILENT_UNTIL_S, COUNT_UNTIL_S)]
    expected_lines = [f'COUNTER-{second:03d}' for second in counted_seconds]
    assert re.findall(r'COUNTER-\d{3}', redirected) == expected_lines, redirected
    # The platform closed the stream during the silence, so the lines after it came over a reopened stream.
    assert stream.call_count >= 2, f'The log stream was opened {stream.call_count} time(s).'
