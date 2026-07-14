from __future__ import annotations

import gzip
import json
from typing import TYPE_CHECKING

import brotli
import pytest
from werkzeug import Request, Response

from apify_client import ApifyClient, ApifyClientAsync

if TYPE_CHECKING:
    from pytest_httpserver import HTTPServer

    from apify_client.types import HttpCompressionAlgorithm

_MOCKED_RUN_ID = 'test_run_id'
_CHARGE_PATH = f'/v2/actor-runs/{_MOCKED_RUN_ID}/charge'


def _decode_body(request: Request) -> dict:
    raw = request.get_data()
    encoding = request.headers.get('Content-Encoding')
    if encoding == 'br':
        raw = brotli.decompress(raw)
    elif encoding == 'gzip':
        raw = gzip.decompress(raw)
    return json.loads(raw)


@pytest.mark.parametrize('encoding', ['gzip', 'brotli'])
@pytest.mark.parametrize(
    'count',
    [0, 1, 5],
)
def test_run_charge_preserves_count_sync(
    httpserver: HTTPServer,
    count: int,
    encoding: HttpCompressionAlgorithm,
) -> None:
    """Ensure `count` is sent as-is (in particular, `0` is preserved), regardless of the request-body encoding."""
    captured_requests: list[Request] = []

    def capture_request(request: Request) -> Response:
        captured_requests.append(request)
        return Response(status=200, mimetype='application/json')

    httpserver.expect_request(_CHARGE_PATH, method='POST').respond_with_handler(capture_request)

    api_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClient(token='test_token', api_url=api_url, encoding=encoding)

    client.run(_MOCKED_RUN_ID).charge('test-event', count=count)

    assert len(captured_requests) == 1
    body = _decode_body(captured_requests[0])
    assert body['count'] == count


@pytest.mark.parametrize('encoding', ['gzip', 'brotli'])
@pytest.mark.parametrize(
    'count',
    [0, 1, 5],
)
async def test_run_charge_preserves_count_async(
    httpserver: HTTPServer,
    count: int,
    encoding: HttpCompressionAlgorithm,
) -> None:
    """Async variant of `test_run_charge_preserves_count_sync`."""
    captured_requests: list[Request] = []

    def capture_request(request: Request) -> Response:
        captured_requests.append(request)
        return Response(status=200, mimetype='application/json')

    httpserver.expect_request(_CHARGE_PATH, method='POST').respond_with_handler(capture_request)

    api_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClientAsync(token='test_token', api_url=api_url, encoding=encoding)

    await client.run(_MOCKED_RUN_ID).charge('test-event', count=count)

    assert len(captured_requests) == 1
    body = _decode_body(captured_requests[0])
    assert body['count'] == count
