from __future__ import annotations

import gzip
import io
from typing import TYPE_CHECKING, Any

import brotli
import pytest
from werkzeug import Request, Response

from apify_client import ApifyClient, ApifyClientAsync

if TYPE_CHECKING:
    from collections.abc import Callable

    from pytest_httpserver import HTTPServer

    from apify_client.types import HttpCompressionAlgorithm

_MOCKED_KVS_ID = 'test_kvs_id'
_RECORD_PATH = f'/v2/key-value-stores/{_MOCKED_KVS_ID}/records/f'


class DuckTypedReader:
    """A file-like object that is not an `io.IOBase`, so only duck-typed detection picks it up."""

    def read(self) -> bytes:
        return b'buffer data'


# The values are built by a factory because reading consumes them, and each case runs once per compression
# algorithm. Each case is (value factory, expected uploaded body, expected content type).
_FILE_LIKE_VALUE_CASES = [
    pytest.param(lambda: io.BytesIO(b'buffer data'), b'buffer data', 'application/octet-stream', id='bytes io'),
    pytest.param(lambda: io.StringIO('buffer data'), b'buffer data', 'text/plain; charset=utf-8', id='string io'),
    pytest.param(DuckTypedReader, b'buffer data', 'application/octet-stream', id='duck-typed reader'),
]


@pytest.fixture(
    params=[
        pytest.param(('gzip', 'gzip'), id='gzip'),
        pytest.param(('brotli', 'br'), id='brotli'),
    ]
)
def compression_case(request: pytest.FixtureRequest) -> tuple[HttpCompressionAlgorithm, str]:
    """Run each test over both supported request-body compression algorithms, as (algorithm, content-encoding)."""
    return request.param


@pytest.fixture
def api_url(httpserver: HTTPServer) -> str:
    """The base URL of the mock server, in the form the clients expect."""
    return httpserver.url_for('/').removesuffix('/')


@pytest.fixture
def captured_records(httpserver: HTTPServer) -> list[Request]:
    """Answer record uploads with a 201 and collect the requests the client sent."""
    requests: list[Request] = []

    def capture_request(request: Request) -> Response:
        requests.append(request)
        return Response(status=201)

    httpserver.expect_request(_RECORD_PATH, method='PUT').respond_with_handler(capture_request)
    return requests


def decode_body(request: Request) -> bytes:
    """Decompress a captured request body according to its `Content-Encoding`."""
    raw = request.get_data()
    encoding = request.headers.get('Content-Encoding')
    if encoding == 'gzip':
        return gzip.decompress(raw)
    if encoding == 'br':
        return brotli.decompress(raw)
    return raw


@pytest.mark.parametrize(('make_value', 'expected_body', 'expected_content_type'), _FILE_LIKE_VALUE_CASES)
def test_set_record_reads_file_like_value_sync(
    *,
    api_url: str,
    captured_records: list[Request],
    compression_case: tuple[HttpCompressionAlgorithm, str],
    make_value: Callable[[], Any],
    expected_body: bytes,
    expected_content_type: str,
) -> None:
    """A file-like value is read and its bytes are uploaded, not passed through unread."""
    algorithm, content_encoding = compression_case
    client = ApifyClient(token='test_token', api_url=api_url, compression=algorithm)

    client.key_value_store(_MOCKED_KVS_ID).set_record('f', make_value())

    assert len(captured_records) == 1
    assert captured_records[0].headers['content-encoding'] == content_encoding
    assert decode_body(captured_records[0]) == expected_body
    assert captured_records[0].headers['content-type'] == expected_content_type


@pytest.mark.parametrize(('make_value', 'expected_body', 'expected_content_type'), _FILE_LIKE_VALUE_CASES)
async def test_set_record_reads_file_like_value_async(
    *,
    api_url: str,
    captured_records: list[Request],
    compression_case: tuple[HttpCompressionAlgorithm, str],
    make_value: Callable[[], Any],
    expected_body: bytes,
    expected_content_type: str,
) -> None:
    """A file-like value is read and its bytes are uploaded, not passed through unread."""
    algorithm, content_encoding = compression_case
    client = ApifyClientAsync(token='test_token', api_url=api_url, compression=algorithm)

    await client.key_value_store(_MOCKED_KVS_ID).set_record('f', make_value())

    assert len(captured_records) == 1
    assert captured_records[0].headers['content-encoding'] == content_encoding
    assert decode_body(captured_records[0]) == expected_body
    assert captured_records[0].headers['content-type'] == expected_content_type
