from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest
from werkzeug import Request, Response

from apify_client import ApifyClient, ApifyClientAsync

if TYPE_CHECKING:
    from collections.abc import Callable

    from pytest_httpserver import HTTPServer

pytestmark = pytest.mark.usefixtures('http_client_classes')

_QUEUE_ID = 'test-queue-id'
_REQUEST_ID = 'test-request-id'
_HEAD_LOCK_PATH = f'/v2/request-queues/{_QUEUE_ID}/head/lock'
_REQUEST_LOCK_PATH = f'/v2/request-queues/{_QUEUE_ID}/requests/{_REQUEST_ID}/lock'
_HEAD_LOCK_RESPONSE = {
    'data': {
        'limit': 1,
        'queueModifiedAt': '2024-01-01T00:00:00.000Z',
        'hadMultipleClients': False,
        'lockSecs': 60,
        'queueHasLockedRequests': True,
        'clientKey': 'test-client-key',
        'items': [],
    }
}
_REQUEST_LOCK_RESPONSE = {'data': {'lockExpiresAt': '2024-01-01T00:01:00.000Z'}}


def _capture_into(captured_requests: list[Request], body: dict) -> Callable[[Request], Response]:
    def handler(request: Request) -> Response:
        captured_requests.append(request)
        return Response(status=200, response=json.dumps(body), mimetype='application/json')

    return handler


def test_list_and_lock_head_sends_lock_secs_sync(httpserver: HTTPServer) -> None:
    """`list_and_lock_head()` passes the lock length straight through as the `lockSecs` query parameter."""
    captured_requests: list[Request] = []
    httpserver.expect_request(_HEAD_LOCK_PATH, method='POST').respond_with_handler(
        _capture_into(captured_requests, _HEAD_LOCK_RESPONSE)
    )
    client = ApifyClient(token='test-token', api_url=httpserver.url_for('/').removesuffix('/'))

    head = client.request_queue(_QUEUE_ID).list_and_lock_head(lock_secs=60, limit=1)

    assert head.lock_secs == 60
    assert len(captured_requests) == 1
    assert captured_requests[0].args['lockSecs'] == '60'
    assert captured_requests[0].args['limit'] == '1'


async def test_list_and_lock_head_sends_lock_secs_async(httpserver: HTTPServer) -> None:
    """Async variant of `test_list_and_lock_head_sends_lock_secs_sync`."""
    captured_requests: list[Request] = []
    httpserver.expect_request(_HEAD_LOCK_PATH, method='POST').respond_with_handler(
        _capture_into(captured_requests, _HEAD_LOCK_RESPONSE)
    )
    client = ApifyClientAsync(token='test-token', api_url=httpserver.url_for('/').removesuffix('/'))

    head = await client.request_queue(_QUEUE_ID).list_and_lock_head(lock_secs=60, limit=1)

    assert head.lock_secs == 60
    assert len(captured_requests) == 1
    assert captured_requests[0].args['lockSecs'] == '60'
    assert captured_requests[0].args['limit'] == '1'


def test_prolong_request_lock_sends_lock_secs_sync(httpserver: HTTPServer) -> None:
    """`prolong_request_lock()` passes the lock length straight through as the `lockSecs` query parameter."""
    captured_requests: list[Request] = []
    httpserver.expect_request(_REQUEST_LOCK_PATH, method='PUT').respond_with_handler(
        _capture_into(captured_requests, _REQUEST_LOCK_RESPONSE)
    )
    client = ApifyClient(token='test-token', api_url=httpserver.url_for('/').removesuffix('/'))

    lock_info = client.request_queue(_QUEUE_ID).prolong_request_lock(_REQUEST_ID, lock_secs=120, forefront=True)

    assert lock_info is not None
    assert len(captured_requests) == 1
    assert captured_requests[0].args['lockSecs'] == '120'
    assert captured_requests[0].args['forefront'] == 'true'


async def test_prolong_request_lock_sends_lock_secs_async(httpserver: HTTPServer) -> None:
    """Async variant of `test_prolong_request_lock_sends_lock_secs_sync`."""
    captured_requests: list[Request] = []
    httpserver.expect_request(_REQUEST_LOCK_PATH, method='PUT').respond_with_handler(
        _capture_into(captured_requests, _REQUEST_LOCK_RESPONSE)
    )
    client = ApifyClientAsync(token='test-token', api_url=httpserver.url_for('/').removesuffix('/'))

    lock_info = await client.request_queue(_QUEUE_ID).prolong_request_lock(_REQUEST_ID, lock_secs=120, forefront=True)

    assert lock_info is not None
    assert len(captured_requests) == 1
    assert captured_requests[0].args['lockSecs'] == '120'
    assert captured_requests[0].args['forefront'] == 'true'
