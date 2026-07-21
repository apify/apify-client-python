from __future__ import annotations

import gzip
import io
from typing import TYPE_CHECKING

from werkzeug import Request, Response

from apify_client import ApifyClient, ApifyClientAsync

if TYPE_CHECKING:
    from pytest_httpserver import HTTPServer

_MOCKED_KVS_ID = 'test_kvs_id'
_RECORD_PATH = f'/v2/key-value-stores/{_MOCKED_KVS_ID}/records/f'


def decode_body(request: Request) -> bytes:
    raw = request.get_data()
    return gzip.decompress(raw) if request.headers.get('Content-Encoding') == 'gzip' else raw


def test_set_record_reads_file_like_value_sync(httpserver: HTTPServer) -> None:
    """Regression test: a file-like value is read and its bytes are uploaded, not passed through unread."""
    captured_requests: list[Request] = []

    def capture_request(request: Request) -> Response:
        captured_requests.append(request)
        return Response(status=201)

    httpserver.expect_request(_RECORD_PATH, method='PUT').respond_with_handler(capture_request)

    api_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClient(token='test_token', api_url=api_url)

    client.key_value_store(_MOCKED_KVS_ID).set_record('f', io.BytesIO(b'buffer data'))

    assert len(captured_requests) == 1
    assert decode_body(captured_requests[0]) == b'buffer data'
    assert captured_requests[0].headers['content-type'] == 'application/octet-stream'


async def test_set_record_reads_file_like_value_async(httpserver: HTTPServer) -> None:
    """Regression test: a file-like value is read and its bytes are uploaded, not passed through unread."""
    captured_requests: list[Request] = []

    def capture_request(request: Request) -> Response:
        captured_requests.append(request)
        return Response(status=201)

    httpserver.expect_request(_RECORD_PATH, method='PUT').respond_with_handler(capture_request)

    api_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClientAsync(token='test_token', api_url=api_url)

    await client.key_value_store(_MOCKED_KVS_ID).set_record('f', io.BytesIO(b'buffer data'))

    assert len(captured_requests) == 1
    assert decode_body(captured_requests[0]) == b'buffer data'
    assert captured_requests[0].headers['content-type'] == 'application/octet-stream'


def test_set_record_reads_stringio_value_sync(httpserver: HTTPServer) -> None:
    """Regression test: a text file-like value is read and uploaded as text/plain through the HTTP stack."""
    captured_requests: list[Request] = []

    def capture_request(request: Request) -> Response:
        captured_requests.append(request)
        return Response(status=201)

    httpserver.expect_request(_RECORD_PATH, method='PUT').respond_with_handler(capture_request)

    api_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClient(token='test_token', api_url=api_url)

    client.key_value_store(_MOCKED_KVS_ID).set_record('f', io.StringIO('buffer data'))

    assert len(captured_requests) == 1
    assert decode_body(captured_requests[0]) == b'buffer data'
    assert captured_requests[0].headers['content-type'] == 'text/plain; charset=utf-8'
