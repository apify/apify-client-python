import asyncio
import json
import logging
import time
from collections.abc import AsyncIterator

import httpx
import respx


from apify_client import ApifyClientAsync
from apify_client.clients import RunClientAsync


@respx.mock
async def test_redirected_logs(caplog) -> None:
    """Test that redirected logs are formatted correctly."""
    mocked_actor_logs_logs = (
        b"2025-05-13T07:24:12.588Z ACTOR: Pulling Docker image of build.\n"
        b"2025-05-13T07:24:12.686Z ACTOR: Creating Docker container.\n"
        b"2025-05-13T07:24:12.745Z ACTOR: Starting Docker container.", # Several logs merged into one message
        b"2025-05-13T07:24:14.132Z [apify] INFO multiline \n log",
        b"2025-05-13T07:25:14.132Z [apify] WARNING some warning",
        b"2025-05-13T07:26:14.132Z [apify] DEBUG c")
    mocked_actor_name = "mocked_actor"
    mocked_run_id = "mocked_run_id"

    expected_logs_and_levels = [
        ("2025-05-13T07:24:12.588Z ACTOR: Pulling Docker image of build.", logging.INFO),
        ("2025-05-13T07:24:12.686Z ACTOR: Creating Docker container.", logging.INFO),
        ("2025-05-13T07:24:12.745Z ACTOR: Starting Docker container.", logging.INFO),
        ("2025-05-13T07:24:14.132Z [apify] INFO multiline \n log", logging.INFO),
        ("2025-05-13T07:25:14.132Z [apify] WARNING some warning", logging.WARNING),
        ("2025-05-13T07:26:14.132Z [apify] DEBUG c", logging.DEBUG),
    ]

    class AsyncByteStream:
        async def __aiter__(self) -> AsyncIterator[bytes]:
            for i in mocked_actor_logs_logs:
                yield i
                await asyncio.sleep(0.1)

        async def aclose(self) -> None:
            pass

    respx.get(url=f'https://example.com/v2/actor-runs/{mocked_run_id}').mock(
        return_value=httpx.Response(content=json.dumps({"data":{'id': mocked_run_id}}),status_code=200))
    respx.get(url=f'https://example.com/v2/actor-runs/{mocked_run_id}/log?stream=1').mock(
        return_value=httpx.Response(stream=AsyncByteStream(), status_code=200))

    run_client = ApifyClientAsync(token="mocked_token", api_url='https://example.com').run(run_id=mocked_run_id)
    streamed_log = await run_client.get_streamed_log(actor_name=mocked_actor_name)

    # Set `propagate=True` during the tests, so that caplog can see the logs..
    logger_name = f"apify.{mocked_actor_name}-{mocked_run_id}"
    logging.getLogger(logger_name).propagate = True

    with caplog.at_level(logging.DEBUG, logger=logger_name):
        async with streamed_log:
            # Do stuff while the log from the other actor is being redirected to the logs.
            await asyncio.sleep(1)

    records = caplog.records
    assert len(records) == 6
    for expected_log_and_level, record in zip(expected_logs_and_levels, records):
        assert expected_log_and_level[0] == record.message
        assert expected_log_and_level[1] == record.levelno
