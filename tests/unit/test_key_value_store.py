from __future__ import annotations

import gzip
import io
import zlib
from typing import TYPE_CHECKING, Any

import brotli
import pytest
from werkzeug import Request, Response

from apify_client import ApifyClient, ApifyClientAsync
from apify_client._consts import MIN_COMPRESSION_SIZE

if TYPE_CHECKING:
    from collections.abc import Callable

    from pytest_httpserver import HTTPServer

    from apify_client.types import HttpCompressionAlgorithm

_MOCKED_KVS_ID = 'test_kvs_id'
_RECORD_PATH = f'/v2/key-value-stores/{_MOCKED_KVS_ID}/records/f'

# The client compresses only bodies of at least `MIN_COMPRESSION_SIZE` bytes, so the value is padded past that
# to keep the compression axis meaningful. A shorter one would go out uncompressed under either algorithm.
_TEXT_VALUE = 'buffer data' + '.' * MIN_COMPRESSION_SIZE
_BYTES_VALUE = _TEXT_VALUE.encode('utf-8')


class DuckTypedReader:
    """A file-like object that is not an `io.IOBase`, so only duck-typed detection picks it up."""

    def read(self) -> bytes:
        return _BYTES_VALUE


# The values are built by a factory because reading consumes them, and each case runs once per compression
# algorithm. Each case is (value factory, expected uploaded body, expected content type).
_FILE_LIKE_VALUE_CASES = [
    pytest.param(lambda: io.BytesIO(_BYTES_VALUE), _BYTES_VALUE, 'application/octet-stream', id='bytes io'),
    pytest.param(lambda: io.StringIO(_TEXT_VALUE), _BYTES_VALUE, 'text/plain; charset=utf-8', id='string io'),
    pytest.param(DuckTypedReader, _BYTES_VALUE, 'application/octet-stream', id='duck-typed reader'),
]

# Each case is (content encoding passed to `set_record`, the body the caller hands over already encoded that way).
_PRE_ENCODED_VALUE_CASES = [
    pytest.param('gzip', gzip.compress(_BYTES_VALUE), id='gzip'),
    pytest.param('br', brotli.compress(_BYTES_VALUE), id='brotli'),
    pytest.param('deflate', zlib.compress(_BYTES_VALUE), id='encoding the client has no compressor for'),
    pytest.param('identity', _BYTES_VALUE, id='identity opt-out'),
]

# Values that cannot be carrying the `gzip` encoding the caller declares for them. Built by a factory for the
# same reason as `_FILE_LIKE_VALUE_CASES`, as the sync and async test each consume their own value.
_INCOMPRESSIBLE_VALUE_CASES = [
    pytest.param(lambda: _TEXT_VALUE, id='string'),
    pytest.param(lambda: {'key': 'value'}, id='json-serializable object'),
    pytest.param(lambda: io.StringIO(_TEXT_VALUE), id='text-mode file-like'),
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


@pytest.mark.parametrize(('content_encoding', 'value'), _PRE_ENCODED_VALUE_CASES)
def test_set_record_uploads_pre_encoded_value_sync(
    *,
    api_url: str,
    captured_records: list[Request],
    compression_case: tuple[HttpCompressionAlgorithm, str],
    content_encoding: str,
    value: bytes,
) -> None:
    """An explicit `content_encoding` uploads the value as it is, whichever compressor the client uses."""
    algorithm, _client_encoding = compression_case
    client = ApifyClient(token='test_token', api_url=api_url, compression=algorithm)

    client.key_value_store(_MOCKED_KVS_ID).set_record(
        'f',
        value,
        content_type='application/octet-stream',
        content_encoding=content_encoding,
    )

    assert len(captured_records) == 1
    assert captured_records[0].headers['content-encoding'] == content_encoding
    assert captured_records[0].get_data() == value


@pytest.mark.parametrize(('content_encoding', 'value'), _PRE_ENCODED_VALUE_CASES)
async def test_set_record_uploads_pre_encoded_value_async(
    *,
    api_url: str,
    captured_records: list[Request],
    compression_case: tuple[HttpCompressionAlgorithm, str],
    content_encoding: str,
    value: bytes,
) -> None:
    """An explicit `content_encoding` uploads the value as it is, whichever compressor the client uses."""
    algorithm, _client_encoding = compression_case
    client = ApifyClientAsync(token='test_token', api_url=api_url, compression=algorithm)

    await client.key_value_store(_MOCKED_KVS_ID).set_record(
        'f',
        value,
        content_type='application/octet-stream',
        content_encoding=content_encoding,
    )

    assert len(captured_records) == 1
    assert captured_records[0].headers['content-encoding'] == content_encoding
    assert captured_records[0].get_data() == value


@pytest.mark.parametrize('make_value', _INCOMPRESSIBLE_VALUE_CASES)
def test_set_record_rejects_declared_compression_of_non_bytes_value_sync(
    *,
    api_url: str,
    captured_records: list[Request],
    make_value: Callable[[], Any],
) -> None:
    """A value that cannot be compressed is rejected before the request, not uploaded under a misleading header."""
    client = ApifyClient(token='test_token', api_url=api_url)

    with pytest.raises(TypeError, match='declares the value is already compressed'):
        client.key_value_store(_MOCKED_KVS_ID).set_record('f', make_value(), content_encoding='gzip')

    assert captured_records == []


@pytest.mark.parametrize('make_value', _INCOMPRESSIBLE_VALUE_CASES)
async def test_set_record_rejects_declared_compression_of_non_bytes_value_async(
    *,
    api_url: str,
    captured_records: list[Request],
    make_value: Callable[[], Any],
) -> None:
    """A value that cannot be compressed is rejected before the request, not uploaded under a misleading header."""
    client = ApifyClientAsync(token='test_token', api_url=api_url)

    with pytest.raises(TypeError, match='declares the value is already compressed'):
        await client.key_value_store(_MOCKED_KVS_ID).set_record('f', make_value(), content_encoding='gzip')

    assert captured_records == []
