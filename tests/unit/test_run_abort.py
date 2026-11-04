from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest
from werkzeug import Request, Response

from apify_client import ApifyClient, ApifyClientAsync

if TYPE_CHECKING:
    from pytest_httpserver import HTTPServer

pytestmark = pytest.mark.usefixtures('http_client_classes')

_MOCKED_RUN_ID = 'test_run_id'
_ABORT_PATH = f'/v2/actor-runs/{_MOCKED_RUN_ID}/abort'
_RUN_RESPONSE = {
    'data': {
        'id': _MOCKED_RUN_ID,
        'actId': 'test_actor_id',
        'userId': 'test_user_id',
        'startedAt': '2024-01-01T00:00:00.000Z',
        'status': 'ABORTING',
        'meta': {'origin': 'API'},
        'stats': {},
        'options': {'build': 'latest', 'timeoutSecs': 3600, 'memoryMbytes': 1024, 'diskMbytes': 2048},
        'buildId': 'test_build_id',
        'defaultKeyValueStoreId': 'test_kvs_id',
        'defaultDatasetId': 'test_dataset_id',
        'defaultRequestQueueId': 'test_rq_id',
        'containerUrl': 'https://example.com',
    }
}


@pytest.mark.parametrize(
    ('gracefully', 'expected_body'),
    [
        pytest.param(None, {}, id='default'),
        pytest.param(True, {'gracefully': True}, id='graceful'),
        pytest.param(False, {'gracefully': False}, id='forced'),
    ],
)
def test_run_abort_sends_gracefully_in_body_sync(
    httpserver: HTTPServer,
    *,
    gracefully: bool | None,
    expected_body: dict,
) -> None:
    """The graceful flag travels in the JSON body and is left out when the caller did not set it."""
    captured_requests: list[Request] = []

    def capture_request(request: Request) -> Response:
        captured_requests.append(request)
        return Response(status=200, response=json.dumps(_RUN_RESPONSE), mimetype='application/json')

    httpserver.expect_request(_ABORT_PATH, method='POST').respond_with_handler(capture_request)

    api_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClient(token='test_token', api_url=api_url)

    run = client.run(_MOCKED_RUN_ID).abort(gracefully=gracefully)

    assert run.id == _MOCKED_RUN_ID
    assert len(captured_requests) == 1
    assert 'gracefully' not in captured_requests[0].args
    assert json.loads(captured_requests[0].get_data()) == expected_body


@pytest.mark.parametrize(
    ('gracefully', 'expected_body'),
    [
        pytest.param(None, {}, id='default'),
        pytest.param(True, {'gracefully': True}, id='graceful'),
        pytest.param(False, {'gracefully': False}, id='forced'),
    ],
)
async def test_run_abort_sends_gracefully_in_body_async(
    httpserver: HTTPServer,
    *,
    gracefully: bool | None,
    expected_body: dict,
) -> None:
    """Async variant of `test_run_abort_sends_gracefully_in_body_sync`."""
    captured_requests: list[Request] = []

    def capture_request(request: Request) -> Response:
        captured_requests.append(request)
        return Response(status=200, response=json.dumps(_RUN_RESPONSE), mimetype='application/json')

    httpserver.expect_request(_ABORT_PATH, method='POST').respond_with_handler(capture_request)

    api_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClientAsync(token='test_token', api_url=api_url)

    run = await client.run(_MOCKED_RUN_ID).abort(gracefully=gracefully)

    assert run.id == _MOCKED_RUN_ID
    assert len(captured_requests) == 1
    assert 'gracefully' not in captured_requests[0].args
    assert json.loads(captured_requests[0].get_data()) == expected_body
