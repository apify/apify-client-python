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
    mocked_actor_logs_logs = (b"INFO a", b"WARNING b", b"DEBUG c")
    mocked_actor_name = "mocked_actor"

    class AsyncByteStream:
        async def __aiter__(self) -> AsyncIterator[bytes]:
            for i in mocked_actor_logs_logs:
                yield i
                await asyncio.sleep(0.1)

        async def aclose(self) -> None:
            pass

    run_client = ApifyClientAsync(token="mocked_token", api_url='https://example.com').run(run_id="run_is_mocked")
    respx.get(url='https://example.com/v2/actor-runs/run_is_mocked').mock(
        return_value=httpx.Response(content=json.dumps({"data":{'actId': 'SbjD4JEucMevUdQAH'}}),status_code=200))
    respx.get(url='https://example.com/v2/actor-runs/run_is_mocked/log?stream=1').mock(
        return_value=httpx.Response(stream=AsyncByteStream(), status_code=200))
        # {'http_version': b'HTTP/1.1', 'network_stream': <httpcore._backends.anyio.AnyIOStream object at 0x7fc82543db70>, 'reason_phrase': b'OK'}
        # [(b'Date', b'Mon, 12 May 2025 13:24:41 GMT'), (b'Content-Type', b'application/json; charset=utf-8'), (b'Transfer-Encoding', b'chunked'), (b'Connection', b'keep-alive'), (b'Cache-Control', b'no-cache, no-store, must-revalidate'), (b'Pragma', b'no-cache'), (b'Expires', b'0'), (b'Access-Control-Allow-Origin', b'*'), (b'Access-Control-Allow-Headers', b'User-Agent, Content-Type, Authorization, X-Apify-Request-Origin, openai-conversation-id, openai-ephemeral-user-id'), (b'Access-Control-Allow-Methods', b'GET, POST'), (b'Access-Control-Expose-Headers', b'X-Apify-Pagination-Total, X-Apify-Pagination-Offset, X-Apify-Pagination-Desc, X-Apify-Pagination-Count, X-Apify-Pagination-Limit'), (b'Referrer-Policy', b'no-referrer'), (b'X-Robots-Tag', b'none'), (b'X-RateLimit-Limit', b'200'), (b'Location', b'https://api.apify.com/v2/actor-runs/ywNUnFFbOksQLa4mH'), (b'Vary', b'Accept-Encoding'), (b'Content-Encoding', b'gzip')]
    streamed_log = await run_client.get_streamed_log(actor_name=mocked_actor_name)

    with caplog.at_level(logging.DEBUG):
        async with streamed_log:
            await asyncio.sleep(1)
            # do some stuff
            pass

    records = caplog.records
    assert len(records) == 2



"""

{'actId': 'SbjD4JEucMevUdQAH', 'buildId': 'Jv7iIjo1JV0gEXQEm', 'buildNumber': '0.0.5', 'containerUrl': 'https://tlo2axp6qbc7.runs.apify.net', 'defaultDatasetId': 'DZq6uDwZ4gSXev8h2', 'defaultKeyValueStoreId': '7UswAGyvNKFGlddHS', 'defaultRequestQueueId': 'Gk4ye89GRCoqFNdsM', 'finishedAt': None, 'generalAccess': 'FOLLOW_USER_SETTING', 'id': 'u6Q52apBHWO09NjDP', 'meta': {'origin': 'API', 'userAgent': 'ApifyClient/1.9.0 (linux; Python/3.10.12); isAtHome/False'}, 'options': {'build': 'latest', 'diskMbytes': 2048, 'memoryMbytes': 1024, 'timeoutSecs': 3600}, 'startedAt': '2025-05-12T13:54:23.028Z', 'stats': {'computeUnits': 0, 'inputBodyLen': 15, 'migrationCount': 0, 'rebootCount': 0, 'restartCount': 0, 'resurrectCount': 0}, 'status': 'READY', 'usage': {'ACTOR_COMPUTE_UNITS': 0, 'DATASET_READS': 0, 'DATASET_WRITES': 0, 'DATA_TRANSFER_EXTERNAL_GBYTES': 0, 'DATA_TRANSFER_INTERNAL_GBYTES': 0, 'KEY_VALUE_STORE_LISTS': 0, 'KEY_VALUE_STORE_READS': 0, 'KEY_VALUE_STORE_WRITES': 1, 'PROXY_RESIDENTIAL_TRANSFER_GBYTES': 0, 'PROXY_SERPS': 0, 'REQUEST_QUEUE_READS': 0, 'REQUEST_QUEUE_WRITES': 0}, 'usageTotalUsd': 5e-05, 'usageUsd': {'ACTOR_COMPUTE_UNITS': 0, 'DATASET_READS': 0, 'DATASET_WRITES': 0, 'DATA_TRANSFER_EXTERNAL_GBYTES': 0, 'DATA_TRANSFER_INTERNAL_GBYTES': 0, 'KEY_VALUE_STORE_LISTS': 0, 'KEY_VALUE_STORE_READS': 0, 'KEY_VALUE_STORE_WRITES': 5e-05, 'PROXY_RESIDENTIAL_TRANSFER_GBYTES': 0, 'PROXY_SERPS': 0, 'REQUEST_QUEUE_READS': 0, 'REQUEST_QUEUE_WRITES': 0}, 'userId': 'LjAzEG1CadliECnrn'}
"""
