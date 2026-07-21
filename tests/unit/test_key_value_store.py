from __future__ import annotations

import gzip
import io
from typing import TYPE_CHECKING

import brotli
import pytest
from werkzeug import Request, Response

from apify_client import ApifyClient, ApifyClientAsync

if TYPE_CHECKING:
    from pytest_httpserver import HTTPServer

    from apify_client.types import HttpCompressionAlgorithm

_MOCKED_KVS_ID = 'test_kvs_id'
_RECORD_PATH = f'/v2/key-value-stores/{_MOCKED_KVS_ID}/records/f'


@pytest.fixture(
    params=[
        pytest.param(('gzip', 'gzip'), id='gzip'),
        pytest.param(('brotli', 'br'), id='brotli'),
    ]
)
def compression_case(request: pytest.FixtureRequest) -> tuple[HttpCompressionAlgorithm, str]:
    """Run each test over both supported request-body compression algorithms, as (algorithm, content-encoding)."""
    return request.param


def decode_body(request: Request) -> bytes:
    """Decompress a captured request body according to its `Content-Encoding`."""
    raw = request.get_data()
    encoding = request.headers.get('Content-Encoding')
    if encoding == 'gzip':
        return gzip.decompress(raw)
    if encoding == 'br':
        return brotli.decompress(raw)
    return raw


def test_set_record_reads_file_like_value_sync(
    httpserver: HTTPServer, compression_case: tuple[HttpCompressionAlgorithm, str]
) -> None:
    """Regression test: a file-like value is read and its bytes are uploaded, not passed through unread."""
    algorithm, content_encoding = compression_case
    captured_requests: list[Request] = []

    def capture_request(request: Request) -> Response:
        captured_requests.append(request)
        return Response(status=201)

    httpserver.expect_request(_RECORD_PATH, method='PUT').respond_with_handler(capture_request)

    api_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClient(token='test_token', api_url=api_url, compression=algorithm)

    client.key_value_store(_MOCKED_KVS_ID).set_record('f', io.BytesIO(b'buffer data'))

    assert len(captured_requests) == 1
    assert captured_requests[0].headers['content-encoding'] == content_encoding
    assert decode_body(captured_requests[0]) == b'buffer data'
    assert captured_requests[0].headers['content-type'] == 'application/octet-stream'


async def test_set_record_reads_file_like_value_async(
    httpserver: HTTPServer, compression_case: tuple[HttpCompressionAlgorithm, str]
) -> None:
    """Regression test: a file-like value is read and its bytes are uploaded, not passed through unread."""
    algorithm, content_encoding = compression_case
    captured_requests: list[Request] = []

    def capture_request(request: Request) -> Response:
        captured_requests.append(request)
        return Response(status=201)

    httpserver.expect_request(_RECORD_PATH, method='PUT').respond_with_handler(capture_request)

    api_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClientAsync(token='test_token', api_url=api_url, compression=algorithm)

    await client.key_value_store(_MOCKED_KVS_ID).set_record('f', io.BytesIO(b'buffer data'))

    assert len(captured_requests) == 1
    assert captured_requests[0].headers['content-encoding'] == content_encoding
    assert decode_body(captured_requests[0]) == b'buffer data'
    assert captured_requests[0].headers['content-type'] == 'application/octet-stream'


def test_set_record_reads_stringio_value_sync(
    httpserver: HTTPServer, compression_case: tuple[HttpCompressionAlgorithm, str]
) -> None:
    """Regression test: a text file-like value is read and uploaded as text/plain through the HTTP stack."""
    algorithm, content_encoding = compression_case
    captured_requests: list[Request] = []

    def capture_request(request: Request) -> Response:
        captured_requests.append(request)
        return Response(status=201)

    httpserver.expect_request(_RECORD_PATH, method='PUT').respond_with_handler(capture_request)

    api_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClient(token='test_token', api_url=api_url, compression=algorithm)

    client.key_value_store(_MOCKED_KVS_ID).set_record('f', io.StringIO('buffer data'))

    assert len(captured_requests) == 1
    assert captured_requests[0].headers['content-encoding'] == content_encoding
    assert decode_body(captured_requests[0]) == b'buffer data'
    assert captured_requests[0].headers['content-type'] == 'text/plain; charset=utf-8'
