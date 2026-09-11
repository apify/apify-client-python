from __future__ import annotations

import gzip
import io
import zlib
from datetime import timedelta
from typing import TYPE_CHECKING, Any
from unittest.mock import Mock

import brotli
import pytest
from werkzeug import Request, Response

from apify_client import ApifyClient, ApifyClientAsync
from apify_client._consts import MIN_COMPRESSION_SIZE, STREAMED_BODY_CHUNK_SIZE
from apify_client.errors import ApifyApiError

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Callable, Iterator

    from pytest_httpserver import HTTPServer

    from apify_client.types import HttpCompressionAlgorithm

pytestmark = pytest.mark.usefixtures('http_client_classes')

_MOCKED_KVS_ID = 'test_kvs_id'
_RECORD_PATH = f'/v2/key-value-stores/{_MOCKED_KVS_ID}/records/f'

# The client compresses only bodies of at least `MIN_COMPRESSION_SIZE` bytes, so the value is padded past that
# to keep the compression axis meaningful. A shorter one would go out uncompressed under either algorithm.
_TEXT_VALUE = 'buffer data' + '.' * MIN_COMPRESSION_SIZE
_BYTES_VALUE = _TEXT_VALUE.encode('utf-8')


class DuckTypedReader:
    """A file-like object that is not an `io.IOBase`, so only duck-typed detection picks it up."""

    def __init__(self, data: bytes = _BYTES_VALUE) -> None:
        self._buffer = io.BytesIO(data)

    def read(self, size: int = -1) -> bytes:
        return self._buffer.read(size)


class AsyncDuckTypedReader:
    """A file-like object with a coroutine `read`, as `aiofiles` provides."""

    def __init__(self, data: bytes = _BYTES_VALUE) -> None:
        self._buffer = io.BytesIO(data)

    async def read(self, size: int = -1) -> bytes:
        return self._buffer.read(size)


class RecordingReader:
    """A file-like object that records the size of every read it serves."""

    def __init__(self, data: bytes) -> None:
        self._buffer = io.BytesIO(data)
        self.read_sizes: list[int] = []

    def read(self, size: int = -1) -> bytes:
        self.read_sizes.append(size)
        return self._buffer.read(size)


class FailingReader:
    """A file-like object whose second read fails, like a disk error halfway through a file."""

    def __init__(self) -> None:
        self._reads = 0

    def read(self, size: int = -1) -> bytes:
        _ = size
        self._reads += 1
        if self._reads > 1:
            raise OSError('disk on fire')
        return b'first chunk'


def bytes_chunks() -> Iterator[bytes]:
    yield _BYTES_VALUE[:100]
    yield _BYTES_VALUE[100:]


async def async_bytes_chunks() -> AsyncIterator[bytes]:
    yield _BYTES_VALUE[:100]
    yield _BYTES_VALUE[100:]


# The values are built by a factory because streaming consumes them, and each case runs once per compression
# algorithm and transport. Each case is (value factory, expected content type); every value streams `_BYTES_VALUE`.
_STREAMED_VALUE_CASES = [
    pytest.param(lambda: io.BytesIO(_BYTES_VALUE), 'application/octet-stream', id='binary file-like'),
    pytest.param(lambda: io.StringIO(_TEXT_VALUE), 'text/plain; charset=utf-8', id='text-mode file-like'),
    pytest.param(DuckTypedReader, 'application/octet-stream', id='duck-typed reader'),
    pytest.param(bytes_chunks, 'application/octet-stream', id='bytes iterator'),
    pytest.param(lambda: iter([_TEXT_VALUE[:100], _TEXT_VALUE[100:]]), 'application/octet-stream', id='str iterator'),
]

# Sources only the asynchronous client can consume.
_ASYNC_STREAMED_VALUE_CASES = [
    pytest.param(async_bytes_chunks, id='async bytes iterator'),
    pytest.param(AsyncDuckTypedReader, id='async file-like'),
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


def assert_streamed_upload(request: Request, expected_content_type: str, body: bytes = _BYTES_VALUE) -> None:
    """Check that a captured upload arrived chunked, uncompressed, and complete."""
    assert request.headers.get('transfer-encoding') == 'chunked'
    assert 'content-encoding' not in request.headers
    assert request.headers['content-type'] == expected_content_type
    assert request.get_data() == body


@pytest.fixture
def flaky_records(httpserver: HTTPServer) -> list[Request]:
    """Fail the first record upload with a 500 and accept the rest, collecting the requests the client sent."""
    requests: list[Request] = []

    def handle_request(request: Request) -> Response:
        requests.append(request)
        return Response(status=500 if len(requests) == 1 else 201)

    httpserver.expect_request(_RECORD_PATH, method='PUT').respond_with_handler(handle_request)
    return requests


@pytest.mark.parametrize(('make_value', 'expected_content_type'), _STREAMED_VALUE_CASES)
def test_set_record_streams_value_sync(
    *,
    api_url: str,
    captured_records: list[Request],
    compression_case: tuple[HttpCompressionAlgorithm, str],
    make_value: Callable[[], Any],
    expected_content_type: str,
) -> None:
    """A streamed value is uploaded in chunks as it is read, and never compressed, whichever compressor is set."""
    algorithm, _content_encoding = compression_case
    client = ApifyClient(token='test_token', api_url=api_url, compression=algorithm)

    client.key_value_store(_MOCKED_KVS_ID).set_record('f', make_value())

    assert len(captured_records) == 1
    assert_streamed_upload(captured_records[0], expected_content_type)


@pytest.mark.parametrize(('make_value', 'expected_content_type'), _STREAMED_VALUE_CASES)
async def test_set_record_streams_value_async(
    *,
    api_url: str,
    captured_records: list[Request],
    compression_case: tuple[HttpCompressionAlgorithm, str],
    make_value: Callable[[], Any],
    expected_content_type: str,
) -> None:
    """A streamed value is uploaded in chunks as it is read, and never compressed, whichever compressor is set."""
    algorithm, _content_encoding = compression_case
    client = ApifyClientAsync(token='test_token', api_url=api_url, compression=algorithm)

    await client.key_value_store(_MOCKED_KVS_ID).set_record('f', make_value())

    assert len(captured_records) == 1
    assert_streamed_upload(captured_records[0], expected_content_type)


@pytest.mark.parametrize('make_value', _ASYNC_STREAMED_VALUE_CASES)
async def test_set_record_streams_async_value_async(
    *,
    api_url: str,
    captured_records: list[Request],
    make_value: Callable[[], Any],
) -> None:
    """The asynchronous client streams an async iterator or an async file-like value as it produces chunks."""
    client = ApifyClientAsync(token='test_token', api_url=api_url)

    await client.key_value_store(_MOCKED_KVS_ID).set_record('f', make_value())

    assert len(captured_records) == 1
    assert_streamed_upload(captured_records[0], 'application/octet-stream')


@pytest.mark.parametrize('make_value', _ASYNC_STREAMED_VALUE_CASES)
def test_set_record_rejects_async_value_sync(
    *,
    api_url: str,
    captured_records: list[Request],
    make_value: Callable[[], Any],
) -> None:
    """The synchronous client cannot consume an asynchronous source, and the error names the client that can."""
    client = ApifyClient(token='test_token', api_url=api_url)

    with pytest.raises(TypeError, match='Use `ApifyClientAsync`'):
        client.key_value_store(_MOCKED_KVS_ID).set_record('f', make_value())

    assert captured_records == []


def test_set_record_reads_file_like_value_in_chunks_sync(*, api_url: str, captured_records: list[Request]) -> None:
    """A file-like value is read in `STREAMED_BODY_CHUNK_SIZE` pieces, never whole."""
    data = b'x' * (STREAMED_BODY_CHUNK_SIZE * 2 + 1)
    reader = RecordingReader(data)
    client = ApifyClient(token='test_token', api_url=api_url)

    client.key_value_store(_MOCKED_KVS_ID).set_record('f', reader)

    # Three reads deliver the data, and a fourth, empty one ends the body.
    assert reader.read_sizes == [STREAMED_BODY_CHUNK_SIZE] * 4
    assert captured_records[0].get_data() == data


async def test_set_record_reads_file_like_value_in_chunks_async(
    *, api_url: str, captured_records: list[Request]
) -> None:
    """A file-like value is read in `STREAMED_BODY_CHUNK_SIZE` pieces, never whole."""
    data = b'x' * (STREAMED_BODY_CHUNK_SIZE * 2 + 1)
    reader = RecordingReader(data)
    client = ApifyClientAsync(token='test_token', api_url=api_url)

    await client.key_value_store(_MOCKED_KVS_ID).set_record('f', reader)

    assert reader.read_sizes == [STREAMED_BODY_CHUNK_SIZE] * 4
    assert captured_records[0].get_data() == data


_SOURCE_RECORD_PATH = '/v2/key-value-stores/source_kvs_id/records/f'


def test_set_record_pipes_streamed_record_sync(
    *, httpserver: HTTPServer, api_url: str, captured_records: list[Request]
) -> None:
    """A record streamed from one store is uploaded to another as it downloads, under its own content type."""
    httpserver.expect_request(_SOURCE_RECORD_PATH, method='GET').respond_with_data(
        _BYTES_VALUE, content_type='text/csv'
    )
    client = ApifyClient(token='test_token', api_url=api_url)

    with client.key_value_store('source_kvs_id').stream_record('f') as record:
        assert record is not None
        client.key_value_store(_MOCKED_KVS_ID).set_record('f', record['value'], content_type=record['content_type'])

    assert len(captured_records) == 1
    assert_streamed_upload(captured_records[0], record['content_type'])


async def test_set_record_pipes_streamed_record_async(
    *, httpserver: HTTPServer, api_url: str, captured_records: list[Request]
) -> None:
    """A record streamed from one store is uploaded to another as it downloads, under its own content type."""
    httpserver.expect_request(_SOURCE_RECORD_PATH, method='GET').respond_with_data(
        _BYTES_VALUE, content_type='text/csv'
    )
    client = ApifyClientAsync(token='test_token', api_url=api_url)

    async with client.key_value_store('source_kvs_id').stream_record('f') as record:
        assert record is not None
        await client.key_value_store(_MOCKED_KVS_ID).set_record(
            'f', record['value'], content_type=record['content_type']
        )

    assert len(captured_records) == 1
    assert_streamed_upload(captured_records[0], record['content_type'])


def test_set_record_retries_seekable_file_like_value_sync(*, api_url: str, flaky_records: list[Request]) -> None:
    """A seekable file-like value is rewound to where it started, so the retry uploads the same bytes again."""
    buffer = io.BytesIO(b'skip' + _BYTES_VALUE)
    buffer.read(4)
    client = ApifyClient(token='test_token', api_url=api_url, min_delay_between_retries=timedelta(milliseconds=1))

    client.key_value_store(_MOCKED_KVS_ID).set_record('f', buffer)

    assert [request.get_data() for request in flaky_records] == [_BYTES_VALUE, _BYTES_VALUE]


async def test_set_record_retries_seekable_file_like_value_async(*, api_url: str, flaky_records: list[Request]) -> None:
    """A seekable file-like value is rewound to where it started, so the retry uploads the same bytes again."""
    buffer = io.BytesIO(b'skip' + _BYTES_VALUE)
    buffer.read(4)
    client = ApifyClientAsync(token='test_token', api_url=api_url, min_delay_between_retries=timedelta(milliseconds=1))

    await client.key_value_store(_MOCKED_KVS_ID).set_record('f', buffer)

    assert [request.get_data() for request in flaky_records] == [_BYTES_VALUE, _BYTES_VALUE]


def test_set_record_does_not_retry_non_rewindable_value_sync(*, api_url: str, flaky_records: list[Request]) -> None:
    """An iterator is consumed by the attempt that sends it, so a failed upload is not retried."""
    client = ApifyClient(token='test_token', api_url=api_url, min_delay_between_retries=timedelta(milliseconds=1))

    with pytest.raises(ApifyApiError):
        client.key_value_store(_MOCKED_KVS_ID).set_record('f', bytes_chunks())

    assert len(flaky_records) == 1


async def test_set_record_does_not_retry_non_rewindable_value_async(
    *, api_url: str, flaky_records: list[Request]
) -> None:
    """An iterator is consumed by the attempt that sends it, so a failed upload is not retried."""
    client = ApifyClientAsync(token='test_token', api_url=api_url, min_delay_between_retries=timedelta(milliseconds=1))

    with pytest.raises(ApifyApiError):
        await client.key_value_store(_MOCKED_KVS_ID).set_record('f', bytes_chunks())

    assert len(flaky_records) == 1


@pytest.mark.usefixtures('captured_records')
def test_set_record_raises_source_error_sync(*, api_url: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """A value that fails mid-upload surfaces its own error after a single attempt, not a retried transport error."""
    client = ApifyClient(token='test_token', api_url=api_url, min_delay_between_retries=timedelta(milliseconds=1))
    send_request = Mock(wraps=client.http_client.send_request)
    monkeypatch.setattr(client.http_client, 'send_request', send_request)

    with pytest.raises(OSError, match='disk on fire'):
        client.key_value_store(_MOCKED_KVS_ID).set_record('f', FailingReader())

    send_request.assert_called_once()


@pytest.mark.usefixtures('captured_records')
async def test_set_record_raises_source_error_async(*, api_url: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """A value that fails mid-upload surfaces its own error after a single attempt, not a retried transport error."""
    client = ApifyClientAsync(token='test_token', api_url=api_url, min_delay_between_retries=timedelta(milliseconds=1))
    send_request = Mock(wraps=client.http_client.send_request)
    monkeypatch.setattr(client.http_client, 'send_request', send_request)

    with pytest.raises(OSError, match='disk on fire'):
        await client.key_value_store(_MOCKED_KVS_ID).set_record('f', FailingReader())

    send_request.assert_called_once()


def test_set_record_streams_pre_encoded_file_like_value_sync(*, api_url: str, captured_records: list[Request]) -> None:
    """A pre-compressed file streams under the caller's `Content-Encoding`, with nothing compressed twice."""
    compressed = gzip.compress(_BYTES_VALUE)
    client = ApifyClient(token='test_token', api_url=api_url)

    client.key_value_store(_MOCKED_KVS_ID).set_record(
        'f', io.BytesIO(compressed), content_type='text/plain', content_encoding='gzip'
    )

    assert captured_records[0].headers['content-encoding'] == 'gzip'
    assert captured_records[0].get_data() == compressed


async def test_set_record_streams_pre_encoded_file_like_value_async(
    *, api_url: str, captured_records: list[Request]
) -> None:
    """A pre-compressed file streams under the caller's `Content-Encoding`, with nothing compressed twice."""
    compressed = gzip.compress(_BYTES_VALUE)
    client = ApifyClientAsync(token='test_token', api_url=api_url)

    await client.key_value_store(_MOCKED_KVS_ID).set_record(
        'f', io.BytesIO(compressed), content_type='text/plain', content_encoding='gzip'
    )

    assert captured_records[0].headers['content-encoding'] == 'gzip'
    assert captured_records[0].get_data() == compressed
