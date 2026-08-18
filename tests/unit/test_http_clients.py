from __future__ import annotations

import asyncio
import gzip
import json
import threading
import time
from datetime import UTC, datetime, timedelta
from io import BytesIO
from typing import TYPE_CHECKING, cast
from unittest.mock import AsyncMock, Mock

import brotli
import impit
import pytest

from apify_client._consts import MIN_COMPRESSION_SIZE
from apify_client._statistics import ClientStatistics
from apify_client.errors import InvalidResponseBodyError
from apify_client.http_clients import (
    HttpClient,
    HttpClientAsync,
    HttpResponse,
    ImpitHttpClient,
    ImpitHttpClientAsync,
)
from apify_client.http_compressors._base import HttpCompressor
from apify_client.http_compressors._brotli import BrotliHttpCompressor
from apify_client.http_compressors._gzip import GzipHttpCompressor

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any

    from apify_client.types import JsonSerializable


class ConcreteHttpClient(HttpClient):
    """Minimal concrete HttpClient for testing base class helpers, relying on the hook defaults."""


class CallOnlyHttpClient(HttpClient):
    """Custom client written against the pre-hook contract, overriding `call` and nothing else."""

    def call(self, **kwargs: Any) -> HttpResponse:
        _ = kwargs
        return Mock(status_code=200)


class CallOnlyHttpClientAsync(HttpClientAsync):
    """Asynchronous counterpart of `CallOnlyHttpClient`."""

    async def call(self, **kwargs: Any) -> HttpResponse:
        _ = kwargs
        return Mock(status_code=200)


def test_call_only_http_client_keeps_working() -> None:
    """A client that only overrides `call` still instantiates and inherits the hook defaults."""
    with CallOnlyHttpClient() as client:
        assert client.call(method='GET', url='https://example.com').status_code == 200
        assert client.is_timeout_error(TimeoutError('test'))
        assert not client.is_retryable_transport_error(TimeoutError('test'))


async def test_call_only_http_client_async_keeps_working() -> None:
    """The asynchronous base is equally tolerant of a client that only overrides `call`."""
    async with CallOnlyHttpClientAsync() as client:
        response = await client.call(method='GET', url='https://example.com')
        assert response.status_code == 200
        assert client.is_timeout_error(TimeoutError('test'))
        assert not client.is_retryable_transport_error(TimeoutError('test'))


def test_retry_with_exp_backoff(http_client_class: type[HttpClient]) -> None:
    attempt_counter = 0

    class RetryableError(Exception):
        pass

    class NonRetryableError(Exception):
        pass

    def returns_on_fifth_attempt(_stop_retrying: Callable, attempt: int) -> Any:
        nonlocal attempt_counter
        attempt_counter += 1

        if attempt == 5:
            return 'SUCCESS'
        raise RetryableError

    def bails_on_third_attempt(stop_retrying: Callable, attempt: int) -> Any:
        nonlocal attempt_counter
        attempt_counter += 1

        if attempt == 3:
            stop_retrying()
            raise NonRetryableError
        else:  # noqa: RET506
            raise RetryableError

    # Returns the correct result after the correct time (should take 100 + 200 + 400 + 800 = 1500 ms)
    start = time.time()
    result = http_client_class._retry_with_exp_backoff(
        returns_on_fifth_attempt, backoff_base=timedelta(milliseconds=100), backoff_factor=2, random_factor=0
    )
    elapsed_time_seconds = time.time() - start
    assert result == 'SUCCESS'
    assert attempt_counter == 5
    assert elapsed_time_seconds > 1.4
    assert elapsed_time_seconds < 3.0

    # Stops retrying when failed for max_retries times
    attempt_counter = 0
    with pytest.raises(RetryableError):
        http_client_class._retry_with_exp_backoff(
            returns_on_fifth_attempt, max_retries=3, backoff_base=timedelta(milliseconds=1)
        )
    assert attempt_counter == 4

    # Bails when the bail function is called
    attempt_counter = 0
    with pytest.raises(NonRetryableError):
        http_client_class._retry_with_exp_backoff(bails_on_third_attempt, backoff_base=timedelta(milliseconds=1))
    assert attempt_counter == 3


async def test_retry_with_exp_backoff_async(
    http_client_async_class: type[HttpClientAsync],
) -> None:
    attempt_counter = 0

    class RetryableError(Exception):
        pass

    class NonRetryableError(Exception):
        pass

    async def returns_on_fifth_attempt(_stop_retrying: Callable, attempt: int) -> Any:
        nonlocal attempt_counter
        attempt_counter += 1

        if attempt == 5:
            return 'SUCCESS'
        raise RetryableError

    async def bails_on_third_attempt(stop_retrying: Callable, attempt: int) -> Any:
        nonlocal attempt_counter
        attempt_counter += 1

        if attempt == 3:
            stop_retrying()
            raise NonRetryableError
        else:  # noqa: RET506
            raise RetryableError

    # Returns the correct result after the correct time (should take 100 + 200 + 400 + 800 = 1500 ms)
    start = time.time()
    result = await http_client_async_class._retry_with_exp_backoff(
        returns_on_fifth_attempt, backoff_base=timedelta(milliseconds=100), backoff_factor=2, random_factor=0
    )
    elapsed_time_seconds = time.time() - start
    assert result == 'SUCCESS'
    assert attempt_counter == 5
    assert elapsed_time_seconds > 1.4
    assert elapsed_time_seconds < 3.0

    # Stops retrying when failed for max_retries times
    attempt_counter = 0
    with pytest.raises(RetryableError):
        await http_client_async_class._retry_with_exp_backoff(
            returns_on_fifth_attempt, max_retries=3, backoff_base=timedelta(milliseconds=1)
        )
    assert attempt_counter == 4

    # Bails when the bail function is called
    attempt_counter = 0
    with pytest.raises(NonRetryableError):
        await http_client_async_class._retry_with_exp_backoff(
            bails_on_third_attempt, backoff_base=timedelta(milliseconds=1)
        )
    assert attempt_counter == 3


def test_base_http_client_initialization() -> None:
    """Test HttpClient initialization with various configurations."""
    statistics = ClientStatistics()

    client = ConcreteHttpClient(
        token='test_token',
        timeout_short=timedelta(seconds=30),
        max_retries=5,
        statistics=statistics,
    )

    assert client._timeout_short == timedelta(seconds=30)
    assert client._max_retries == 5
    assert client._statistics == statistics
    assert client._headers is not None
    assert 'Authorization' in client._headers
    assert client._headers['Authorization'] == 'Bearer test_token'

    # Test without statistics (should create default)
    client2 = ConcreteHttpClient(token='test_token')
    assert isinstance(client2._statistics, ClientStatistics)


def test_http_client_init_headers_override_defaults_case_insensitively() -> None:
    """Constructor headers replace same-named default headers even when their casings differ."""
    client = ConcreteHttpClient(token='default_token', headers={'authorization': 'Bearer custom'})

    auth_headers = {key: value for key, value in client._headers.items() if key.lower() == 'authorization'}
    assert auth_headers == {'authorization': 'Bearer custom'}


def test_http_client_init_workflow_key_header(monkeypatch: pytest.MonkeyPatch) -> None:
    """The X-Apify-Workflow-Key default header is set from the APIFY_WORKFLOW_KEY env var."""
    monkeypatch.setenv('APIFY_WORKFLOW_KEY', 'workflow_key_123')

    client = ConcreteHttpClient()

    assert client._headers['X-Apify-Workflow-Key'] == 'workflow_key_123'


def test_set_default_authorization_sets_token_when_missing() -> None:
    """set_default_authorization sets the Bearer token when no authorization header is configured."""
    client = ConcreteHttpClient()

    client.set_default_authorization('test_token')

    assert client._headers['Authorization'] == 'Bearer test_token'


@pytest.mark.parametrize(
    ('base', 'override', 'expected'),
    [
        pytest.param(None, None, {}, id='both none'),
        pytest.param({'Accept': 'a'}, None, {'Accept': 'a'}, id='override none'),
        pytest.param(None, {'Accept': 'a'}, {'Accept': 'a'}, id='base none'),
        pytest.param({'Accept': 'a'}, {'X-Custom': 'b'}, {'Accept': 'a', 'X-Custom': 'b'}, id='disjoint names'),
        pytest.param({'Authorization': 'x'}, {'Authorization': 'y'}, {'Authorization': 'y'}, id='same casing'),
        pytest.param({'Authorization': 'x'}, {'authorization': 'y'}, {'authorization': 'y'}, id='lowercase override'),
        pytest.param({'authorization': 'x'}, {'AUTHORIZATION': 'y'}, {'AUTHORIZATION': 'y'}, id='uppercase override'),
    ],
)
def test_merge_headers(
    base: dict[str, str] | None,
    override: dict[str, str] | None,
    expected: dict[str, str],
) -> None:
    """_merge_headers merges case-insensitively, override values win and keep their casing."""
    assert HttpClient._merge_headers(base, override) == expected


def test_http_client_creates_sync_impit_client() -> None:
    """The synchronous adapter creates the underlying Impit client and releases it on close."""
    client = ImpitHttpClient(token='test_token_123')

    assert isinstance(client._impit_client, impit.Client)
    client.close()


async def test_http_client_async_creates_async_impit_client() -> None:
    """The asynchronous adapter creates the underlying Impit client and releases it on close."""
    client = ImpitHttpClientAsync(token='test_token_123')

    assert isinstance(client._impit_async_client, impit.AsyncClient)
    await client.aclose()


def test_parse_params_none() -> None:
    """Test _parse_params with None input."""
    assert HttpClient._parse_params(None) is None


def test_parse_params_boolean() -> None:
    """Test _parse_params converts booleans to `false` or `true`."""
    result = HttpClient._parse_params({'flag': True, 'disabled': False})
    assert result == {'flag': 'true', 'disabled': 'false'}


def test_parse_params_list() -> None:
    """Test _parse_params converts lists to comma-separated strings."""
    result = HttpClient._parse_params({'ids': ['id1', 'id2', 'id3']})
    assert result == {'ids': 'id1,id2,id3'}


def test_parse_params_datetime() -> None:
    """Test _parse_params converts datetime to Zulu format."""
    dt = datetime(2024, 1, 15, 10, 30, 45, 123000, tzinfo=UTC)
    result = HttpClient._parse_params({'created_at': dt})
    assert result == {'created_at': '2024-01-15T10:30:45.123Z'}


@pytest.mark.skipif(not hasattr(time, 'tzset'), reason='time.tzset is Unix-only')
def test_parse_params_naive_datetime_treated_as_utc(monkeypatch: pytest.MonkeyPatch) -> None:
    """Naive datetimes must be treated as UTC, not the host's local timezone."""
    monkeypatch.setenv('TZ', 'Asia/Karachi')
    time.tzset()
    try:
        dt = datetime(2024, 1, 15, 10, 30, 45, 123000)  # noqa: DTZ001 -- intentionally naive
        result = HttpClient._parse_params({'created_at': dt})
        assert result == {'created_at': '2024-01-15T10:30:45.123Z'}
    finally:
        # Restore TZ before re-applying tzset so the test doesn't leak Karachi time to later tests.
        monkeypatch.undo()
        time.tzset()


def test_parse_params_none_values_filtered() -> None:
    """Test _parse_params filters out None values."""
    result = HttpClient._parse_params({'a': 1, 'b': None, 'c': 'value'})
    assert result == {'a': 1, 'c': 'value'}


def test_parse_params_mixed() -> None:
    """Test _parse_params with mixed types."""
    dt = datetime(2024, 1, 15, 10, 30, 45, 123000, tzinfo=UTC)
    result = HttpClient._parse_params(
        {
            'limit': 10,
            'offset': 0,
            'flag': True,
            'tags': ['tag1', 'tag2'],
            'created_at': dt,
            'name': 'test',
            'empty': None,
        }
    )
    assert result == {
        'limit': 10,
        'offset': 0,
        'flag': 'true',
        'tags': 'tag1,tag2',
        'created_at': '2024-01-15T10:30:45.123Z',
        'name': 'test',
    }


RETRYABLE_TRANSPORT_ERRORS = (
    # Impit raises a bare `HTTPError` for a body that ends mid-chunk, so even the generic base class is transient.
    impit.HTTPError,
    impit.TimeoutException,
    impit.NetworkError,
    impit.RemoteProtocolError,
    impit.DecodingError,
    # A proxy rejecting the tunnel is often transient, e.g. one that is overloaded or rate-limiting.
    impit.ProxyError,
)
"""Transport errors that must stay retryable."""

NON_RETRYABLE_TRANSPORT_ERRORS = (
    impit.UnsupportedProtocol,
    impit.LocalProtocolError,
    impit.TooManyRedirects,
)
"""Transport errors that a retry cannot fix, so they must fail on the first attempt.

`impit.HTTPStatusError` belongs here too, but no built-in adapter ever raises it, because `_make_request` decides on
status codes from the response itself.
"""


def test_builtin_http_client_retry_policy() -> None:
    """Transient transport failures are retried, and the ones a retry cannot fix stop the loop immediately."""
    with ImpitHttpClient() as client:
        for error_class in RETRYABLE_TRANSPORT_ERRORS:
            assert client.is_retryable_transport_error(error_class('test')), error_class.__name__

        for error_class in NON_RETRYABLE_TRANSPORT_ERRORS:
            assert not client.is_retryable_transport_error(error_class('test')), error_class.__name__

        # `InvalidResponseBodyError` is the client's own error, raised outside the pipeline - never a transport failure.
        assert not client.is_retryable_transport_error(InvalidResponseBodyError(Mock()))
        assert not client.is_retryable_transport_error(ValueError('test'))


def test_sync_http_client_classifies_timeout_errors() -> None:
    """The built-in synchronous client exposes transport-neutral timeout classification."""
    with ImpitHttpClient() as client:
        assert client.is_timeout_error(TimeoutError('test'))
        assert client.is_timeout_error(impit.TimeoutException('test'))
        assert not client.is_timeout_error(ValueError('test'))


async def test_async_http_client_classifies_timeout_errors() -> None:
    """The built-in asynchronous client exposes transport-neutral timeout classification."""
    async with ImpitHttpClientAsync() as client:
        assert client.is_timeout_error(TimeoutError('test'))
        assert client.is_timeout_error(impit.TimeoutException('test'))
        assert not client.is_timeout_error(ValueError('test'))


@pytest.fixture(
    params=[
        pytest.param((GzipHttpCompressor(), 'gzip', gzip.decompress), id='gzip'),
        pytest.param((BrotliHttpCompressor(), 'br', brotli.decompress), id='brotli'),
    ]
)
def compressor_case(request: pytest.FixtureRequest) -> tuple:
    return request.param


def test_prepare_request_call_basic() -> None:
    """Test _prepare_request_call returns the client default headers when no per-request values are given."""
    client = ConcreteHttpClient(token='test_token')

    headers, params, data = client._prepare_request_call()
    assert headers == client._headers
    assert headers is not client._headers
    assert headers['Authorization'] == 'Bearer test_token'
    assert params is None
    assert data is None


def test_prepare_request_call_with_json() -> None:
    """A small JSON body is serialized and typed, but sent uncompressed and without a `Content-Encoding`."""
    client = ConcreteHttpClient()

    json_data = {'key': 'value', 'number': 42}
    headers, _params, data = client._prepare_request_call(json=json_data)

    assert headers['Content-Type'] == 'application/json'
    assert data == b'{"key": "value", "number": 42}'
    assert not any(key.lower() == 'content-encoding' for key in headers)


@pytest.mark.parametrize(
    ('json_body', 'expected'),
    [
        pytest.param({}, b'{}', id='empty dict'),
        pytest.param([], b'[]', id='empty list'),
        pytest.param(0, b'0', id='zero'),
        pytest.param(False, b'false', id='false'),
        pytest.param('', b'""', id='empty string'),
    ],
)
def test_prepare_request_call_with_falsy_json(json_body: JsonSerializable, expected: bytes) -> None:
    """A falsy but valid JSON body is still serialized and sent, rather than treated as no body at all."""
    client = ConcreteHttpClient()

    headers, _params, data = client._prepare_request_call(json=json_body)

    assert headers['Content-Type'] == 'application/json'
    assert data == expected


@pytest.mark.parametrize(
    'data',
    [
        pytest.param('test string', id='str'),
        pytest.param(b'test bytes', id='bytes'),
        pytest.param(bytearray(b'test bytearray'), id='bytearray'),
    ],
)
def test_prepare_request_call_with_data(data: str | bytes | bytearray) -> None:
    """A raw body of any accepted type is normalized to bytes."""
    client = ConcreteHttpClient()

    _headers, _params, prepared = client._prepare_request_call(data=data)

    expected = data.encode('utf-8') if isinstance(data, str) else bytes(data)
    assert prepared == expected


@pytest.mark.parametrize(
    'body_size',
    [
        pytest.param(MIN_COMPRESSION_SIZE, id='at threshold'),
        pytest.param(MIN_COMPRESSION_SIZE + 1, id='above threshold'),
        pytest.param(MIN_COMPRESSION_SIZE * 16, id='well above threshold'),
    ],
)
def test_prepare_request_call_compresses_body_at_or_above_threshold(
    compressor_case: tuple,
    body_size: int,
) -> None:
    """A raw body of at least `MIN_COMPRESSION_SIZE` bytes is compressed and labeled with its encoding."""
    compressor, content_encoding, decompress = compressor_case
    client = ConcreteHttpClient(http_compressor=compressor)
    body = b'x' * body_size

    headers, _params, data = client._prepare_request_call(data=body)

    assert headers['Content-Encoding'] == content_encoding
    assert decompress(data) == body


@pytest.mark.parametrize(
    'body_size',
    [
        pytest.param(0, id='empty'),
        pytest.param(1, id='single byte'),
        pytest.param(MIN_COMPRESSION_SIZE - 1, id='just below threshold'),
    ],
)
def test_prepare_request_call_skips_compression_below_threshold(compressor_case: tuple, body_size: int) -> None:
    """A raw body under `MIN_COMPRESSION_SIZE` is sent verbatim with no `Content-Encoding`, whichever compressor."""
    compressor, _content_encoding, _decompress = compressor_case
    client = ConcreteHttpClient(http_compressor=compressor)
    body = b'x' * body_size

    headers, _params, data = client._prepare_request_call(data=body)

    assert data == body
    assert not any(key.lower() == 'content-encoding' for key in headers)


def test_prepare_request_call_compresses_bytearray_data(compressor_case: tuple) -> None:
    """A `bytearray` body above the threshold is compressed without error (regression: needs bytes conversion)."""
    compressor, content_encoding, decompress = compressor_case
    client = ConcreteHttpClient(http_compressor=compressor)
    body = bytearray(b'test bytearray' * 128)

    headers, _params, data = client._prepare_request_call(data=body)

    assert headers['Content-Encoding'] == content_encoding
    assert decompress(data) == bytes(body)


def test_prepare_request_call_compresses_json_above_threshold(compressor_case: tuple) -> None:
    """A JSON body that serializes to at least `MIN_COMPRESSION_SIZE` bytes is compressed."""
    compressor, content_encoding, decompress = compressor_case
    client = ConcreteHttpClient(http_compressor=compressor)
    json_data = {'key': 'x' * MIN_COMPRESSION_SIZE}

    headers, _params, data = client._prepare_request_call(json=json_data)

    assert headers['Content-Type'] == 'application/json'
    assert headers['Content-Encoding'] == content_encoding
    assert json.loads(decompress(data)) == json_data


def test_prepare_request_call_measures_threshold_in_bytes_not_characters(compressor_case: tuple) -> None:
    """A `str` body under the threshold in characters but over it in UTF-8 bytes is still compressed."""
    compressor, content_encoding, decompress = compressor_case
    client = ConcreteHttpClient(http_compressor=compressor)
    # U+00E9 encodes to 2 bytes, so this body is under the threshold in characters but over it in bytes.
    body = '\u00e9' * (MIN_COMPRESSION_SIZE // 2 + 1)

    headers, _params, data = client._prepare_request_call(data=body)

    assert headers['Content-Encoding'] == content_encoding
    assert decompress(data) == body.encode('utf-8')


@pytest.mark.parametrize(
    'data',
    [
        pytest.param(b'x' * MIN_COMPRESSION_SIZE, id='bytes at threshold'),
        pytest.param(bytearray(b'x' * MIN_COMPRESSION_SIZE), id='bytearray at threshold'),
        pytest.param('x' * MIN_COMPRESSION_SIZE, id='ascii str at threshold'),
        pytest.param('\u00e9' * (MIN_COMPRESSION_SIZE // 2 + 1), id='multibyte str above byte threshold'),
    ],
)
def test_is_body_worth_compressing(data: Any) -> None:
    """The gate reports a body `_prepare_request_call` would compress, judging a `str` by its encoded bytes."""
    assert ConcreteHttpClient._is_body_worth_compressing(data)


@pytest.mark.parametrize(
    'data',
    [
        pytest.param(None, id='no body'),
        pytest.param(b'x' * (MIN_COMPRESSION_SIZE - 1), id='bytes below threshold'),
        pytest.param('x' * (MIN_COMPRESSION_SIZE - 1), id='ascii str below threshold'),
        pytest.param(BytesIO(b'x' * MIN_COMPRESSION_SIZE), id='file-like'),
        pytest.param({'key': 'x' * MIN_COMPRESSION_SIZE}, id='mapping'),
    ],
)
def test_is_body_not_worth_compressing(data: Any) -> None:
    """A body below the threshold, or of a type the client sends as it is, needs no worker-thread hop."""
    assert not ConcreteHttpClient._is_body_worth_compressing(data)


@pytest.mark.parametrize(
    'content_type',
    [
        pytest.param('image/png', id='image'),
        pytest.param('video/mp4', id='video'),
        pytest.param('application/zip', id='archive'),
    ],
)
def test_prepare_request_call_skips_compression_for_already_compressed_content(content_type: str) -> None:
    """An already-compressed body is sent verbatim, carries no `Content-Encoding`, and keeps every other header."""
    client = ConcreteHttpClient(token='test_token', http_compressor=GzipHttpCompressor())
    # Above the size threshold, so the content type is what skips compression here.
    payload = b'\x89PNG' + b'\xff' * MIN_COMPRESSION_SIZE

    headers, _params, data = client._prepare_request_call(
        headers={'content-type': content_type},
        data=payload,
    )

    assert data == payload
    assert not any(key.lower() == 'content-encoding' for key in headers)
    assert headers['Authorization'] == 'Bearer test_token'
    assert headers['content-type'] == content_type
    assert headers['User-Agent'] == client._headers['User-Agent']


def test_prepare_request_call_keeps_caller_content_encoding_for_a_file_like_body() -> None:
    """A file-like body skips compression entirely, and its `Content-Encoding` reaches the transport untouched."""
    client = ConcreteHttpClient(http_compressor=GzipHttpCompressor())
    stream = BytesIO(gzip.compress(b'raw payload'))

    headers, _params, data = client._prepare_request_call(
        headers={'content-encoding': 'gzip'},
        data=cast('bytes', stream),
    )

    assert data is stream
    assert headers['content-encoding'] == 'gzip'


@pytest.mark.parametrize(
    'content_type',
    [
        pytest.param('image/svg+xml', id='structured xml suffix'),
        pytest.param('image/bmp', id='raw bitmap'),
        pytest.param('audio/wav', id='raw audio'),
    ],
)
def test_prepare_request_call_compresses_exceptions_to_compressed_prefixes(
    content_type: str,
    compressor_case: tuple,
) -> None:
    """Types that are text or raw are compressed even when they sit under an already-compressed prefix."""
    compressor, content_encoding, decompress = compressor_case
    client = ConcreteHttpClient(http_compressor=compressor)
    payload = b'x' * MIN_COMPRESSION_SIZE

    headers, _params, data = client._prepare_request_call(
        headers={'content-type': content_type},
        data=payload,
    )

    assert headers['Content-Encoding'] == content_encoding
    assert isinstance(data, bytes)
    assert decompress(data) == payload


def test_prepare_request_call_json_and_data_error() -> None:
    """Test _prepare_request_call raises error when both json and data are provided."""
    client = ConcreteHttpClient()

    with pytest.raises(ValueError, match='Cannot pass both "json" and "data" parameters'):
        client._prepare_request_call(json={'key': 'value'}, data='string')


def test_prepare_request_call_with_params() -> None:
    """Test _prepare_request_call parses params correctly."""
    client = ConcreteHttpClient()

    _headers, params, _data = client._prepare_request_call(params={'limit': 10, 'flag': True})

    assert params == {'limit': 10, 'flag': 'true'}


def test_prepare_request_call_does_not_mutate_caller_headers() -> None:
    """Test _prepare_request_call does not mutate the caller's headers dict.

    A caller that reuses a shared headers dict across calls must not see stale
    `Content-Type`/`Content-Encoding` headers leak in from a prior JSON/body call.
    """
    client = ConcreteHttpClient()

    caller_headers = {'x-trace-id': 'abc-123'}
    original = dict(caller_headers)

    client._prepare_request_call(headers=caller_headers, json={'x': 1})
    assert caller_headers == original

    client._prepare_request_call(headers=caller_headers, data='payload')
    assert caller_headers == original


def test_prepare_request_call_per_request_headers_override_defaults_case_insensitively() -> None:
    """A per-request header replaces a same-named default header even when their casings differ."""
    client = ConcreteHttpClient(token='default_token')

    headers, _params, _data = client._prepare_request_call(headers={'authorization': 'Bearer per-request'})

    auth_headers = {key: value for key, value in headers.items() if key.lower() == 'authorization'}
    assert auth_headers == {'authorization': 'Bearer per-request'}


def test_prepare_request_call_json_keeps_caller_content_type() -> None:
    """A caller-supplied content type is not overwritten by the JSON default, regardless of casing."""
    client = ConcreteHttpClient()

    headers, _params, _data = client._prepare_request_call(
        headers={'content-type': 'application/json; charset=utf-8'},
        json={'key': 'value'},
    )

    content_type_headers = {key: value for key, value in headers.items() if key.lower() == 'content-type'}
    assert content_type_headers == {'content-type': 'application/json; charset=utf-8'}


@pytest.mark.parametrize(
    ('caller_headers', 'body'),
    [
        pytest.param({'content-encoding': 'br'}, b'x' * MIN_COMPRESSION_SIZE, id='body the client would compress'),
        pytest.param({'content-encoding': 'br'}, b'payload', id='body below the size threshold'),
        pytest.param(
            {'content-encoding': 'br', 'content-type': 'image/jpeg'},
            b'\xff' * MIN_COMPRESSION_SIZE,
            id='already-compressed content type',
        ),
        pytest.param({'content-encoding': 'identity'}, b'x' * MIN_COMPRESSION_SIZE, id='identity opt-out'),
        pytest.param(
            {'content-encoding': 'deflate'},
            b'x' * MIN_COMPRESSION_SIZE,
            id='encoding the client has no compressor for',
        ),
    ],
)
def test_prepare_request_call_keeps_caller_content_encoding(caller_headers: dict[str, str], body: bytes) -> None:
    """A caller-supplied `Content-Encoding` marks the body as pre-encoded, so it goes out untouched and labeled."""
    client = ConcreteHttpClient(http_compressor=GzipHttpCompressor())

    headers, _params, data = client._prepare_request_call(headers=caller_headers, data=body)

    assert data == body
    encoding_headers = {key: value for key, value in headers.items() if key.lower() == 'content-encoding'}
    assert encoding_headers == {'content-encoding': caller_headers['content-encoding']}


def test_prepare_request_call_keeps_client_wide_content_encoding() -> None:
    """A `Content-Encoding` configured on the client counts as caller-supplied on every request it sends."""
    client = ConcreteHttpClient(headers={'Content-Encoding': 'identity'}, http_compressor=GzipHttpCompressor())
    body = b'x' * MIN_COMPRESSION_SIZE

    headers, _params, data = client._prepare_request_call(data=body)

    assert data == body
    assert headers['Content-Encoding'] == 'identity'


def test_build_url_with_params_none() -> None:
    """Test _build_url_with_params with None params."""
    client = ConcreteHttpClient()

    url = client._build_url_with_params('https://api.test.com/endpoint')
    assert url == 'https://api.test.com/endpoint'


def test_build_url_with_params_simple() -> None:
    """Test _build_url_with_params with simple params."""
    client = ConcreteHttpClient()

    url = client._build_url_with_params('https://api.test.com/endpoint', params={'key': 'value', 'limit': 10})
    assert 'key=value' in url
    assert 'limit=10' in url
    assert url.startswith('https://api.test.com/endpoint?')


def test_build_url_with_params_list() -> None:
    """Test _build_url_with_params with list values."""
    client = ConcreteHttpClient()

    url = client._build_url_with_params('https://api.test.com/endpoint', params={'tags': ['tag1', 'tag2', 'tag3']})
    assert 'tags=tag1' in url
    assert 'tags=tag2' in url
    assert 'tags=tag3' in url


def test_build_url_with_params_mixed() -> None:
    """Test _build_url_with_params with mixed param types."""
    client = ConcreteHttpClient()

    url = client._build_url_with_params(
        'https://api.test.com/endpoint', params={'limit': 10, 'tags': ['a', 'b'], 'name': 'test'}
    )
    assert 'limit=10' in url
    assert 'tags=a' in url
    assert 'tags=b' in url
    assert 'name=test' in url


class _ThreadRecordingCompressor(HttpCompressor):
    """Compressor that records the thread `compress` ran on, to prove the work is offloaded."""

    content_encoding = 'gzip'

    def __init__(self) -> None:
        self.compress_thread_id: int | None = None

    def compress(self, data: bytes) -> bytes:
        self.compress_thread_id = threading.get_ident()
        return gzip.compress(data)


async def test_async_call_compresses_request_body_off_the_event_loop(
    http_client_async_class: type[HttpClientAsync], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Body serialization and compression must run in a worker thread, not block the event loop."""
    compressor = _ThreadRecordingCompressor()
    client = http_client_async_class(token='test_token', http_compressor=compressor)
    monkeypatch.setattr(client, 'send_request', AsyncMock(return_value=Mock(status_code=200)))

    await client.call(
        method='POST',
        url='https://api.test.com/endpoint',
        json={'key': 'x' * MIN_COMPRESSION_SIZE},
    )

    assert compressor.compress_thread_id is not None
    assert compressor.compress_thread_id != threading.get_ident()


async def test_async_call_compresses_a_multibyte_str_body_off_the_event_loop(
    http_client_async_class: type[HttpClientAsync], monkeypatch: pytest.MonkeyPatch
) -> None:
    """A `str` body over the threshold only once encoded is still compressed, so it must be offloaded."""
    compressor = _ThreadRecordingCompressor()
    client = http_client_async_class(token='test_token', http_compressor=compressor)
    monkeypatch.setattr(client, 'send_request', AsyncMock(return_value=Mock(status_code=200)))

    await client.call(
        method='PUT',
        url='https://api.test.com/endpoint',
        data='\u00e9' * (MIN_COMPRESSION_SIZE // 2 + 1),
    )

    assert compressor.compress_thread_id is not None
    assert compressor.compress_thread_id != threading.get_ident()


def _to_thread_spy(monkeypatch: pytest.MonkeyPatch) -> Mock:
    """Patch `asyncio.to_thread` with a `Mock` that still performs the hop, to record whether it was used."""
    spy = Mock(side_effect=asyncio.to_thread)
    monkeypatch.setattr(asyncio, 'to_thread', spy)
    return spy


async def test_async_call_skips_thread_offload_without_a_body(
    http_client_async_class: type[HttpClientAsync], monkeypatch: pytest.MonkeyPatch
) -> None:
    """A bodyless request has nothing to compress, so it must not pay the worker-thread hop."""
    client = http_client_async_class(token='test_token')
    monkeypatch.setattr(client, 'send_request', AsyncMock(return_value=Mock(status_code=200)))
    spy = _to_thread_spy(monkeypatch)

    await client.call(method='GET', url='https://api.test.com/endpoint')

    spy.assert_not_called()


async def test_async_call_skips_thread_offload_for_a_body_below_the_threshold(
    http_client_async_class: type[HttpClientAsync],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A raw body too small to be compressed must not pay the worker-thread hop either."""
    client = http_client_async_class(token='test_token')
    monkeypatch.setattr(client, 'send_request', AsyncMock(return_value=Mock(status_code=200)))
    spy = _to_thread_spy(monkeypatch)

    await client.call(method='PUT', url='https://api.test.com/endpoint', data=b'x' * (MIN_COMPRESSION_SIZE - 1))

    spy.assert_not_called()


async def test_async_call_offloads_a_body_at_the_threshold(
    http_client_async_class: type[HttpClientAsync], monkeypatch: pytest.MonkeyPatch
) -> None:
    """A raw body large enough to be compressed is prepared in a worker thread."""
    client = http_client_async_class(token='test_token')
    monkeypatch.setattr(client, 'send_request', AsyncMock(return_value=Mock(status_code=200)))
    spy = _to_thread_spy(monkeypatch)

    await client.call(method='PUT', url='https://api.test.com/endpoint', data=b'x' * MIN_COMPRESSION_SIZE)

    spy.assert_called_once()


async def test_async_call_skips_thread_offload_for_a_body_it_cannot_compress(
    http_client_async_class: type[HttpClientAsync],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A body of a type the client passes through needs no hop, and deciding that must not need its length."""
    client = http_client_async_class(token='test_token')
    monkeypatch.setattr(client, 'send_request', AsyncMock(return_value=Mock(status_code=200)))
    spy = _to_thread_spy(monkeypatch)

    # `encode_key_value_store_record_value` passes file-like bodies through, so the gate cannot assume a length.
    body: Any = BytesIO(b'x' * MIN_COMPRESSION_SIZE)

    await client.call(method='PUT', url='https://api.test.com/endpoint', data=body)

    spy.assert_not_called()
