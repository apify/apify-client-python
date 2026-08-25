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
_CHARGE_PATH = f'/v2/actor-runs/{_MOCKED_RUN_ID}/charge'


@pytest.mark.parametrize(
    'count',
    [
        pytest.param(0, id='zero'),
        pytest.param(1, id='one'),
        pytest.param(5, id='five'),
    ],
)
def test_run_charge_preserves_count_sync(httpserver: HTTPServer, count: int) -> None:
    """Ensure `count` is sent as-is, in particular that `0` is preserved rather than dropped as falsy."""
    captured_requests: list[Request] = []

    def capture_request(request: Request) -> Response:
        captured_requests.append(request)
        return Response(status=200, mimetype='application/json')

    httpserver.expect_request(_CHARGE_PATH, method='POST').respond_with_handler(capture_request)

    api_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClient(token='test_token', api_url=api_url)

    client.run(_MOCKED_RUN_ID).charge('test-event', count=count)

    assert len(captured_requests) == 1
    body = json.loads(captured_requests[0].get_data())
    assert body['count'] == count


@pytest.mark.parametrize(
    'count',
    [
        pytest.param(0, id='zero'),
        pytest.param(1, id='one'),
        pytest.param(5, id='five'),
    ],
)
async def test_run_charge_preserves_count_async(httpserver: HTTPServer, count: int) -> None:
    """Async variant of `test_run_charge_preserves_count_sync`."""
    captured_requests: list[Request] = []

    def capture_request(request: Request) -> Response:
        captured_requests.append(request)
        return Response(status=200, mimetype='application/json')

    httpserver.expect_request(_CHARGE_PATH, method='POST').respond_with_handler(capture_request)

    api_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClientAsync(token='test_token', api_url=api_url)

    await client.run(_MOCKED_RUN_ID).charge('test-event', count=count)

    assert len(captured_requests) == 1
    body = json.loads(captured_requests[0].get_data())
    assert body['count'] == count
