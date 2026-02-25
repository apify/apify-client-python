from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from datetime import timedelta
from typing import TYPE_CHECKING, Any

import pytest

import apify_client as apify_client_module
from apify_client import (
    ApifyClient,
    ApifyClientAsync,
    HttpClient,
    HttpClientAsync,
    HttpResponse,
)
from apify_client._consts import DEFAULT_MAX_RETRIES, DEFAULT_TIMEOUT
from apify_client._http_clients import ImpitHttpClient, ImpitHttpClientAsync
from apify_client.errors import ApifyApiError

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator

    from pytest_httpserver import HTTPServer


# -- Test response and client implementations --


@dataclass
class FakeResponse:
    """A minimal response object that satisfies the HttpResponse protocol."""

    status_code: int = 200
    text: str = ''
    content: bytes = b''
    headers: dict[str, str] = field(default_factory=dict)
    _json: Any = field(default=None, repr=False)

    def json(self) -> Any:
        return self._json

    def read(self) -> bytes:
        return self.content

    async def aread(self) -> bytes:
        return self.content

    def close(self) -> None:
        pass

    async def aclose(self) -> None:
        pass

    def iter_bytes(self) -> Iterator[bytes]:
        yield self.content

    async def aiter_bytes(self) -> AsyncIterator[bytes]:
        yield self.content


def _make_fake_response() -> FakeResponse:
    """Create a standard fake response for testing."""
    return FakeResponse(
        status_code=200,
        text='{"data": {"id": "test123"}}',
        content=b'{"data": {"id": "test123"}}',
        headers={'content-type': 'application/json'},
        _json={'data': {'id': 'test123'}},
    )


class FakeHttpClient(HttpClient):
    """A custom sync HTTP client for testing."""

    def __init__(self) -> None:
        super().__init__()
        self.calls: list[dict[str, Any]] = []

    def call(
        self,
        *,
        method: str,
        url: str,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        data: str | bytes | bytearray | None = None,
        json: Any = None,
        stream: bool | None = None,
        timeout: timedelta | None = None,
    ) -> FakeResponse:
        self.calls.append(
            {
                'method': method,
                'url': url,
                'headers': headers,
                'params': params,
                'data': data,
                'json': json,
                'stream': stream,
                'timeout': timeout,
            }
        )
        return _make_fake_response()


class FakeHttpClientAsync(HttpClientAsync):
    """A custom async HTTP client for testing."""

    def __init__(self) -> None:
        super().__init__()
        self.calls: list[dict[str, Any]] = []

    async def call(
        self,
        *,
        method: str,
        url: str,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        data: str | bytes | bytearray | None = None,
        json: Any = None,
        stream: bool | None = None,
        timeout: timedelta | None = None,
    ) -> FakeResponse:
        self.calls.append(
            {
                'method': method,
                'url': url,
                'headers': headers,
                'params': params,
                'data': data,
                'json': json,
                'stream': stream,
                'timeout': timeout,
            }
        )
        return _make_fake_response()


# -- Protocol / ABC conformance tests --


def test_fake_response_satisfies_http_response_protocol() -> None:
    """Test that FakeResponse satisfies the HttpResponse protocol."""
    response = FakeResponse()
    assert isinstance(response, HttpResponse)


def test_fake_http_client_is_http_client() -> None:
    """Test that FakeHttpClient is an instance of HttpClient."""
    client = FakeHttpClient()
    assert isinstance(client, HttpClient)


def test_fake_http_client_async_is_http_client_async() -> None:
    """Test that FakeHttpClientAsync is an instance of HttpClientAsync."""
    client = FakeHttpClientAsync()
    assert isinstance(client, HttpClientAsync)


def test_apify_http_client_is_http_client() -> None:
    """Test that ImpitHttpClient is an instance of HttpClient."""
    client = ImpitHttpClient()
    assert isinstance(client, HttpClient)


def test_apify_http_client_async_is_http_client_async() -> None:
    """Test that ImpitHttpClientAsync is an instance of HttpClientAsync."""
    client = ImpitHttpClientAsync()
    assert isinstance(client, HttpClientAsync)


async def test_fake_response_async_methods() -> None:
    """Test that FakeResponse async methods work correctly."""
    response = FakeResponse(content=b'hello')
    assert await response.aread() == b'hello'
    await response.aclose()  # should not raise
    chunks = [chunk async for chunk in response.aiter_bytes()]
    assert chunks == [b'hello']


def test_http_client_abc_not_instantiable() -> None:
    """Test that HttpClient cannot be instantiated directly (it's abstract)."""
    with pytest.raises(TypeError, match='abstract method'):
        HttpClient()


def test_http_client_async_abc_not_instantiable() -> None:
    """Test that HttpClientAsync cannot be instantiated directly (it's abstract)."""
    with pytest.raises(TypeError, match='abstract method'):
        HttpClientAsync()


# -- ApifyClient with custom http_client --


def test_apify_client_accepts_custom_http_client() -> None:
    """Test that ApifyClient accepts a custom http_client parameter."""
    fake_client = FakeHttpClient()
    client = ApifyClient(token='test_token', http_client=fake_client)

    assert client.http_client is fake_client


def test_apify_client_uses_default_http_client_when_none_provided() -> None:
    """Test that ApifyClient creates default ImpitHttpClient when no http_client is provided."""
    client = ApifyClient(token='test_token')

    assert isinstance(client.http_client, ImpitHttpClient)


def test_apify_client_custom_http_client_receives_requests() -> None:
    """Test that requests flow through the custom HTTP client."""
    fake_client = FakeHttpClient()
    client = ApifyClient(token='test_token', http_client=fake_client)

    # Use _get() via the dataset client to avoid Pydantic model validation
    # (actor.get() would try to validate against ActorResponse model)
    result = client.dataset('test-dataset')._get()

    assert len(fake_client.calls) == 1
    call = fake_client.calls[0]
    assert call['method'] == 'GET'
    assert 'test-dataset' in call['url']
    assert result == {'data': {'id': 'test123'}}


def test_apify_client_custom_http_client_ignores_other_params() -> None:
    """Test that timeout/retries/headers params don't affect custom http_client."""
    fake_client = FakeHttpClient()
    client = ApifyClient(
        token='test_token',
        http_client=fake_client,
        timeout=timedelta(seconds=999),
        max_retries=99,
        headers={'X-Custom': 'should-be-ignored'},
    )

    # The custom client should be used as-is
    assert client.http_client is fake_client

    # Verify the custom client retained its own defaults (params were not forwarded)
    assert fake_client._timeout == DEFAULT_TIMEOUT
    assert fake_client._max_retries == DEFAULT_MAX_RETRIES


def test_apify_client_custom_http_client_no_header_warning() -> None:
    """Test that no header warning is raised when custom http_client is provided."""
    fake_client = FakeHttpClient()

    # This should NOT raise a UserWarning even though we pass overriding headers,
    # because headers are ignored when http_client is provided.
    with warnings.catch_warnings():
        warnings.simplefilter('error')
        ApifyClient(
            token='test_token',
            http_client=fake_client,
            headers={'User-Agent': 'Custom/1.0', 'Authorization': 'Bearer custom'},
        )


# -- ApifyClientAsync with custom http_client --


async def test_apify_client_async_accepts_custom_http_client() -> None:
    """Test that ApifyClientAsync accepts a custom http_client parameter."""
    fake_client = FakeHttpClientAsync()
    client = ApifyClientAsync(token='test_token', http_client=fake_client)

    assert client.http_client is fake_client


async def test_apify_client_async_uses_default_http_client_when_none_provided() -> None:
    """Test that ApifyClientAsync creates default ImpitHttpClientAsync when no http_client is provided."""
    client = ApifyClientAsync(token='test_token')

    assert isinstance(client.http_client, ImpitHttpClientAsync)


async def test_apify_client_async_custom_http_client_receives_requests() -> None:
    """Test that async requests flow through the custom HTTP client."""
    fake_client = FakeHttpClientAsync()
    client = ApifyClientAsync(token='test_token', http_client=fake_client)

    # Use _get() via the dataset client to avoid Pydantic model validation
    result = await client.dataset('test-dataset')._get()

    assert len(fake_client.calls) == 1
    call = fake_client.calls[0]
    assert call['method'] == 'GET'
    assert 'test-dataset' in call['url']
    assert result == {'data': {'id': 'test123'}}


# -- Public exports --


def test_public_exports() -> None:
    """Test that all HTTP client types are available from the public API."""
    assert hasattr(apify_client_module, 'HttpClient')
    assert hasattr(apify_client_module, 'HttpClientAsync')
    assert hasattr(apify_client_module, 'HttpResponse')
    assert hasattr(apify_client_module, 'ImpitHttpClient')
    assert hasattr(apify_client_module, 'ImpitHttpClientAsync')


# -- http_client property --


def test_apify_client_http_client_property_returns_correct_type() -> None:
    """Test that http_client property returns the correct type."""
    # With default
    client = ApifyClient(token='test')
    assert isinstance(client.http_client, HttpClient)

    # With custom
    fake = FakeHttpClient()
    client2 = ApifyClient(token='test', http_client=fake)
    assert client2.http_client is fake


async def test_apify_client_async_http_client_property_returns_correct_type() -> None:
    """Test that http_client property returns the correct type for async client."""
    # With default
    client = ApifyClientAsync(token='test')
    assert isinstance(client.http_client, HttpClientAsync)

    # With custom
    fake = FakeHttpClientAsync()
    client2 = ApifyClientAsync(token='test', http_client=fake)
    assert client2.http_client is fake


# -- Error handling with custom http_client --


class ErrorRaisingHttpClient(HttpClient):
    """A custom HTTP client that raises ApifyApiError."""

    def call(self, *, method: str, **_kwargs: Any) -> FakeResponse:
        error_response = FakeResponse(
            status_code=404,
            text='{"error": {"message": "Actor not found", "type": "record-not-found"}}',
            _json={'error': {'message': 'Actor not found', 'type': 'record-not-found'}},
        )
        raise ApifyApiError(error_response, attempt=1, method=method)


def test_custom_http_client_error_handling() -> None:
    """Test that ApifyApiError from custom client is handled correctly by resource clients."""
    error_client = ErrorRaisingHttpClient()
    client = ApifyClient(token='test', http_client=error_client)

    # _get() should catch 404 record-not-found and return None
    result = client.actor('nonexistent').get()
    assert result is None


class ErrorRaisingHttpClientAsync(HttpClientAsync):
    """A custom async HTTP client that raises ApifyApiError."""

    async def call(self, *, method: str, **_kwargs: Any) -> FakeResponse:
        error_response = FakeResponse(
            status_code=404,
            text='{"error": {"message": "Actor not found", "type": "record-not-found"}}',
            _json={'error': {'message': 'Actor not found', 'type': 'record-not-found'}},
        )
        raise ApifyApiError(error_response, attempt=1, method=method)


async def test_custom_http_client_async_error_handling() -> None:
    """Test that ApifyApiError from async custom client is handled correctly by resource clients."""
    error_client = ErrorRaisingHttpClientAsync()
    client = ApifyClientAsync(token='test', http_client=error_client)

    # _get() should catch 404 record-not-found and return None
    result = await client.actor('nonexistent').get()
    assert result is None


# -- Integration with real HTTP server --


def test_custom_http_client_with_real_server(httpserver: HTTPServer) -> None:
    """Test that a custom HTTP client wrapping ImpitHttpClient works with a real server."""
    httpserver.expect_request('/v2/datasets/test-dataset').respond_with_json(
        {'data': {'id': 'test-dataset', 'name': 'My Dataset'}},
    )

    # Create a wrapping client that adds custom headers
    inner_client = ImpitHttpClient(token='test_token')

    class WrappingHttpClient(HttpClient):
        def call(self, *, method: str, url: str, **kwargs: Any) -> HttpResponse:
            if kwargs.get('headers') is None:
                kwargs['headers'] = {}
            kwargs['headers']['X-Custom-Header'] = 'custom-value'
            return inner_client.call(method=method, url=url, **kwargs)

    api_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClient(token='test_token', api_url=api_url, http_client=WrappingHttpClient())

    # Use _get() to test the raw request flow without Pydantic validation
    result = client.dataset('test-dataset')._get()

    assert result is not None
    assert result['data']['id'] == 'test-dataset'


async def test_custom_http_client_async_with_real_server(httpserver: HTTPServer) -> None:
    """Test that a custom async HTTP client wrapping ImpitHttpClientAsync works with a real server."""
    httpserver.expect_request('/v2/datasets/test-dataset').respond_with_json(
        {'data': {'id': 'test-dataset', 'name': 'My Dataset'}},
    )

    # Create a wrapping client that adds custom headers
    inner_client = ImpitHttpClientAsync(token='test_token')

    class WrappingHttpClientAsync(HttpClientAsync):
        async def call(self, *, method: str, url: str, **kwargs: Any) -> HttpResponse:
            if kwargs.get('headers') is None:
                kwargs['headers'] = {}
            kwargs['headers']['X-Custom-Header'] = 'custom-value'
            return await inner_client.call(method=method, url=url, **kwargs)

    api_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClientAsync(token='test_token', api_url=api_url, http_client=WrappingHttpClientAsync())

    # Use _get() to test the raw request flow without Pydantic validation
    result = await client.dataset('test-dataset')._get()

    assert result is not None
    assert result['data']['id'] == 'test-dataset'
