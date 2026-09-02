from __future__ import annotations

import asyncio
import json as jsonlib
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import timedelta
from http.client import HTTPConnection
from textwrap import dedent
from typing import TYPE_CHECKING, Any
from unittest.mock import AsyncMock, Mock
from urllib.parse import urlsplit

import impit
import pytest
from werkzeug import Request, Response

import apify_client as apify_client_module
import apify_client.http_clients as http_clients_module
from apify_client import ApifyClient, ApifyClientAsync
from apify_client.errors import ApifyApiError
from apify_client.http_clients import (
    HttpClient,
    HttpClientAsync,
    HttpResponse,
    ImpitHttpClient,
    ImpitHttpClientAsync,
)

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator

    from pytest_httpserver import HTTPServer

    from apify_client.types import Timeout


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
        timeout: Timeout = 'medium',
    ) -> HttpResponse:
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
        timeout: Timeout = 'medium',
    ) -> HttpResponse:
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


def _stdlib_fetch(
    *,
    method: str,
    url: str,
    headers: dict[str, str],
    content: bytes | None,
    timeout: float | None,
) -> FakeResponse:
    """Send one request over `http.client` and adapt the result to the `HttpResponse` protocol."""
    parts = urlsplit(url)
    connection = HTTPConnection(parts.hostname or 'localhost', parts.port, timeout=timeout)
    try:
        path = f'{parts.path}?{parts.query}' if parts.query else parts.path
        connection.request(method, path, body=content, headers=headers)
        raw = connection.getresponse()
        body = raw.read()
        try:
            parsed = jsonlib.loads(body)
        except ValueError:
            parsed = None
        return FakeResponse(
            status_code=raw.status,
            text=body.decode(),
            content=body,
            headers={key.lower(): value for key, value in raw.getheaders()},
            _json=parsed,
        )
    finally:
        connection.close()


class StdlibHttpClient(HttpClient):
    """A hooks-only custom sync client: implements `send_request` and inherits the shared pipeline."""

    def send_request(
        self,
        *,
        method: str,
        url: str,
        headers: dict[str, str],
        content: bytes | None,
        timeout: float | None,
        stream: bool,
    ) -> HttpResponse:
        _ = stream
        return _stdlib_fetch(method=method, url=url, headers=headers, content=content, timeout=timeout)


class StdlibHttpClientAsync(HttpClientAsync):
    """A hooks-only custom async client: implements `send_request` and inherits the shared pipeline."""

    async def send_request(
        self,
        *,
        method: str,
        url: str,
        headers: dict[str, str],
        content: bytes | None,
        timeout: float | None,
        stream: bool,
    ) -> HttpResponse:
        _ = stream
        return await asyncio.to_thread(
            _stdlib_fetch, method=method, url=url, headers=headers, content=content, timeout=timeout
        )


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


def test_apify_http_client_is_http_client(http_client_class: type[HttpClient]) -> None:
    """Test that each built-in synchronous client is an HttpClient."""
    client = http_client_class()
    assert isinstance(client, HttpClient)


def test_apify_http_client_async_is_http_client_async(http_client_async_class: type[HttpClientAsync]) -> None:
    """Test that each built-in asynchronous client is an HttpClientAsync."""
    client = http_client_async_class()
    assert isinstance(client, HttpClientAsync)


async def test_fake_response_async_methods() -> None:
    """Test that FakeResponse async methods work correctly."""
    response = FakeResponse(content=b'hello')
    assert await response.aread() == b'hello'
    await response.aclose()  # should not raise
    chunks = [chunk async for chunk in response.aiter_bytes()]
    assert chunks == [b'hello']


def test_http_client_without_transport_fails_loudly() -> None:
    """The sync base carries hook defaults, but its inherited `call` still needs a transport implementation."""
    with pytest.raises(NotImplementedError, match='Implement `send_request`'):
        HttpClient().call(method='GET', url='https://example.com')


async def test_http_client_async_without_transport_fails_loudly() -> None:
    """The async base carries hook defaults, but its inherited `call` still needs a transport implementation."""
    with pytest.raises(NotImplementedError, match='Implement `send_request`'):
        await HttpClientAsync().call(method='GET', url='https://example.com')


def test_apify_client_with_custom_http_client() -> None:
    """Test that ApifyClient.with_custom_http_client accepts a custom http_client."""
    fake_client = FakeHttpClient()
    client = ApifyClient.with_custom_http_client(token='test_token', http_client=fake_client)

    assert client.http_client is fake_client


def test_apify_client_uses_default_http_client_when_none_provided() -> None:
    """Test that ApifyClient creates default ImpitHttpClient when no http_client is provided."""
    client = ApifyClient(token='test_token')

    assert isinstance(client.http_client, ImpitHttpClient)


def test_apify_client_custom_http_client_receives_requests() -> None:
    """Test that requests flow through the custom HTTP client."""
    fake_client = FakeHttpClient()
    client = ApifyClient.with_custom_http_client(token='test_token', http_client=fake_client)

    # Use _get() via the dataset client to avoid Pydantic model validation
    # (actor.get() would try to validate against ActorResponse model)
    result = client.dataset('test-dataset')._get(timeout='short')

    assert len(fake_client.calls) == 1
    call = fake_client.calls[0]
    assert call['method'] == 'GET'
    assert 'test-dataset' in call['url']
    assert result == {'data': {'id': 'test123'}}


def test_apify_client_with_custom_http_client_accepts_url_params() -> None:
    """Test that with_custom_http_client can be combined with token, api_url, and api_public_url."""
    fake_client = FakeHttpClient()
    client = ApifyClient.with_custom_http_client(
        token='test_token',
        api_url='https://custom.api.example.com',
        api_public_url='https://public.api.example.com',
        http_client=fake_client,
    )
    assert client.http_client is fake_client


async def test_apify_client_async_with_custom_http_client() -> None:
    """Test that ApifyClientAsync.with_custom_http_client accepts a custom http_client."""
    fake_client = FakeHttpClientAsync()
    client = ApifyClientAsync.with_custom_http_client(token='test_token', http_client=fake_client)

    assert client.http_client is fake_client


async def test_apify_client_async_uses_default_http_client_when_none_provided() -> None:
    """Test that ApifyClientAsync creates default ImpitHttpClientAsync when no http_client is provided."""
    client = ApifyClientAsync(token='test_token')

    assert isinstance(client.http_client, ImpitHttpClientAsync)


async def test_apify_client_async_custom_http_client_receives_requests() -> None:
    """Test that async requests flow through the custom HTTP client."""
    fake_client = FakeHttpClientAsync()
    client = ApifyClientAsync.with_custom_http_client(token='test_token', http_client=fake_client)

    # Use _get() via the dataset client to avoid Pydantic model validation
    result = await client.dataset('test-dataset')._get(timeout='short')

    assert len(fake_client.calls) == 1
    call = fake_client.calls[0]
    assert call['method'] == 'GET'
    assert 'test-dataset' in call['url']
    assert result == {'data': {'id': 'test123'}}


async def test_apify_client_async_with_custom_http_client_accepts_url_params() -> None:
    """Test that async with_custom_http_client can be combined with token, api_url, and api_public_url."""
    fake_client = FakeHttpClientAsync()
    client = ApifyClientAsync.with_custom_http_client(
        token='test_token',
        api_url='https://custom.api.example.com',
        api_public_url='https://public.api.example.com',
        http_client=fake_client,
    )
    assert client.http_client is fake_client


def test_public_exports() -> None:
    """HTTP client types are exposed from `apify_client.http_clients`, not the root namespace."""
    for name in (
        'HttpClient',
        'HttpClientAsync',
        'HttpResponse',
        'Httpx2HttpClient',
        'Httpx2HttpClientAsync',
        'ImpitHttpClient',
        'ImpitHttpClientAsync',
    ):
        assert hasattr(http_clients_module, name)
        assert not hasattr(apify_client_module, name)

    assert not hasattr(http_clients_module, 'HttpClientBase')


def test_httpx_clients_raise_clear_error_when_extra_missing() -> None:
    """Missing HTTPX keeps normal and star imports usable while explicit HTTPX access raises a clear error."""
    script = dedent(
        """
        import sys

        class BlockHttpx2:
            def find_spec(self, name, *_args):
                if name == 'httpx2' or name.startswith('httpx2.'):
                    raise ModuleNotFoundError(f"No module named '{name}'", name='httpx2')
                return None

        sys.meta_path.insert(0, BlockHttpx2())

        import apify_client.http_clients as module
        assert module.HttpClient is not None
        assert module.ImpitHttpClient is not None

        namespace = {}
        exec('from apify_client.http_clients import *', namespace)
        assert namespace['HttpClient'] is module.HttpClient
        assert 'Httpx2HttpClient' not in namespace

        for name in ('Httpx2HttpClient', 'Httpx2HttpClientAsync'):
            try:
                getattr(module, name)
            except ImportError as exc:
                assert "No module named 'httpx2'" in str(exc)
                assert "pip install 'apify-client[httpx2]'" in str(exc)
            else:
                raise AssertionError(f'{name} did not raise ImportError')
        """
    )
    result = subprocess.run(  # noqa: S603
        [sys.executable, '-c', script],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def test_apify_client_http_client_property_returns_correct_type() -> None:
    """Test that http_client property returns the correct type."""
    # With default
    client = ApifyClient(token='test')
    assert isinstance(client.http_client, HttpClient)

    # With custom
    fake = FakeHttpClient()
    client2 = ApifyClient.with_custom_http_client(token='test', http_client=fake)
    assert client2.http_client is fake


async def test_apify_client_async_http_client_property_returns_correct_type() -> None:
    """Test that http_client property returns the correct type for async client."""
    # With default
    client = ApifyClientAsync(token='test')
    assert isinstance(client.http_client, HttpClientAsync)

    # With custom
    fake = FakeHttpClientAsync()
    client2 = ApifyClientAsync.with_custom_http_client(token='test', http_client=fake)
    assert client2.http_client is fake


class ErrorRaisingHttpClient(HttpClient):
    """A custom HTTP client that raises ApifyApiError."""

    def call(self, *, method: str, **_kwargs: Any) -> FakeResponse:
        error_response = FakeResponse(
            status_code=404,
            text='{"error": {"message": "Actor not found", "type": "record-not-found"}}',
            _json={'error': {'message': 'Actor not found', 'type': 'record-not-found'}},
        )
        raise ApifyApiError(error_response, 1, method=method)


def test_custom_http_client_error_handling() -> None:
    """Test that ApifyApiError from custom client is handled correctly by resource clients."""
    error_client = ErrorRaisingHttpClient()
    client = ApifyClient.with_custom_http_client(token='test', http_client=error_client)

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
        raise ApifyApiError(error_response, 1, method=method)


async def test_custom_http_client_async_error_handling() -> None:
    """Test that ApifyApiError from async custom client is handled correctly by resource clients."""
    error_client = ErrorRaisingHttpClientAsync()
    client = ApifyClientAsync.with_custom_http_client(token='test', http_client=error_client)

    # _get() should catch 404 record-not-found and return None
    result = await client.actor('nonexistent').get()
    assert result is None


def test_custom_http_client_with_real_server(httpserver: HTTPServer, http_client_class: type[HttpClient]) -> None:
    """Test that a custom HTTP client wrapping a built-in client works with a real server."""
    httpserver.expect_request('/v2/datasets/test-dataset').respond_with_json(
        {'data': {'id': 'test-dataset', 'name': 'My Dataset'}},
    )

    # Create a wrapping client that adds custom headers
    inner_client = http_client_class(token='test_token')

    class WrappingHttpClient(HttpClient):
        def call(self, *, method: str, url: str, **kwargs: Any) -> HttpResponse:
            if kwargs.get('headers') is None:
                kwargs['headers'] = {}
            kwargs['headers']['X-Custom-Header'] = 'custom-value'
            return inner_client.call(method=method, url=url, **kwargs)

    api_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClient.with_custom_http_client(token='test_token', api_url=api_url, http_client=WrappingHttpClient())

    # Use _get() to test the raw request flow without Pydantic validation
    result = client.dataset('test-dataset')._get(timeout='short')

    assert result is not None
    assert result['data']['id'] == 'test-dataset'


async def test_custom_http_client_async_with_real_server(
    httpserver: HTTPServer, http_client_async_class: type[HttpClientAsync]
) -> None:
    """Test that a custom async HTTP client wrapping a built-in client works with a real server."""
    httpserver.expect_request('/v2/datasets/test-dataset').respond_with_json(
        {'data': {'id': 'test-dataset', 'name': 'My Dataset'}},
    )

    # Create a wrapping client that adds custom headers
    inner_client = http_client_async_class(token='test_token')

    class WrappingHttpClientAsync(HttpClientAsync):
        async def call(self, *, method: str, url: str, **kwargs: Any) -> HttpResponse:
            if kwargs.get('headers') is None:
                kwargs['headers'] = {}
            kwargs['headers']['X-Custom-Header'] = 'custom-value'
            return await inner_client.call(method=method, url=url, **kwargs)

    api_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClientAsync.with_custom_http_client(
        token='test_token', api_url=api_url, http_client=WrappingHttpClientAsync()
    )

    # Use _get() to test the raw request flow without Pydantic validation
    result = await client.dataset('test-dataset')._get(timeout='short')

    assert result is not None
    assert result['data']['id'] == 'test-dataset'


class PreparingHttpClient(HttpClient):
    """A custom sync HTTP client that sends requests prepared by the base-class helpers."""

    def __init__(self, token: str | None = None) -> None:
        super().__init__(token=token)
        self._impit_client = impit.Client()

    def call(
        self,
        *,
        method: str,
        url: str,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        data: str | bytes | bytearray | None = None,
        json: Any = None,
        **_kwargs: Any,
    ) -> HttpResponse:
        headers, params, content = self._prepare_request_call(headers=headers, params=params, data=data, json=json)
        url = self._build_url_with_params(url, params=params)
        return self._impit_client.request(method=method, url=url, headers=headers, content=content)


class PreparingHttpClientAsync(HttpClientAsync):
    """A custom async HTTP client that sends requests prepared by the base-class helpers."""

    def __init__(self, token: str | None = None) -> None:
        super().__init__(token=token)
        self._impit_client = impit.AsyncClient()

    async def call(
        self,
        *,
        method: str,
        url: str,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        data: str | bytes | bytearray | None = None,
        json: Any = None,
        **_kwargs: Any,
    ) -> HttpResponse:
        headers, params, content = self._prepare_request_call(headers=headers, params=params, data=data, json=json)
        url = self._build_url_with_params(url, params=params)
        return await self._impit_client.request(method=method, url=url, headers=headers, content=content)


def _echo_headers(request: Request) -> Response:
    """Respond with the received request headers so tests can assert on them."""
    return Response(
        response=jsonlib.dumps({'received_headers': dict(request.headers)}),
        status=200,
        content_type='application/json',
    )


def test_custom_http_client_sends_token_from_classmethod(httpserver: HTTPServer) -> None:
    """Token passed to with_custom_http_client is sent as the Authorization header by the custom client."""
    httpserver.expect_request('/v2/datasets/test-dataset').respond_with_handler(_echo_headers)

    api_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClient.with_custom_http_client(
        token='test_token',
        api_url=api_url,
        http_client=PreparingHttpClient(),
    )

    result = client.dataset('test-dataset')._get(timeout='short')

    assert result is not None
    assert result['received_headers']['Authorization'] == 'Bearer test_token'


async def test_custom_http_client_async_sends_token_from_classmethod(httpserver: HTTPServer) -> None:
    """Token passed to async with_custom_http_client is sent as the Authorization header by the custom client."""
    httpserver.expect_request('/v2/datasets/test-dataset').respond_with_handler(_echo_headers)

    api_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClientAsync.with_custom_http_client(
        token='test_token',
        api_url=api_url,
        http_client=PreparingHttpClientAsync(),
    )

    result = await client.dataset('test-dataset')._get(timeout='short')

    assert result is not None
    assert result['received_headers']['Authorization'] == 'Bearer test_token'


def test_custom_builtin_http_client_instance_sends_token(
    httpserver: HTTPServer, http_client_class: type[HttpClient]
) -> None:
    """Token from with_custom_http_client reaches the wire for each pre-built tokenless client."""
    httpserver.expect_request('/v2/datasets/test-dataset').respond_with_handler(_echo_headers)

    api_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClient.with_custom_http_client(token='test_token', api_url=api_url, http_client=http_client_class())

    result = client.dataset('test-dataset')._get(timeout='short')

    assert result is not None
    assert result['received_headers']['Authorization'] == 'Bearer test_token'


def test_custom_http_client_keeps_own_token() -> None:
    """An Authorization header configured on the custom client itself is not overridden by with_custom_http_client."""
    http_client = PreparingHttpClient(token='client_token')

    ApifyClient.with_custom_http_client(token='outer_token', http_client=http_client)

    assert http_client._headers['Authorization'] == 'Bearer client_token'


def test_custom_http_client_keeps_differently_cased_authorization() -> None:
    """A lowercase 'authorization' header on the custom client is not duplicated by the token injection."""
    http_client = PreparingHttpClient()
    http_client._headers['authorization'] = 'Bearer client_token'

    ApifyClient.with_custom_http_client(token='outer_token', http_client=http_client)

    assert 'Authorization' not in http_client._headers
    assert http_client._headers['authorization'] == 'Bearer client_token'


def test_hooks_only_client_retries_and_sends_default_headers(httpserver: HTTPServer) -> None:
    """A client implementing only `send_request` inherits header merging and 5xx retries from the shared `call`."""
    auth_headers: list[str | None] = []

    def handler(request: Request) -> Response:
        auth_headers.append(request.headers.get('Authorization'))
        if len(auth_headers) < 3:
            return Response(
                response='{"error": {"type": "internal-error", "message": "Server exploded."}}',
                status=500,
                content_type='application/json',
            )
        return Response(response='{"data": {"id": "abc"}}', status=200, content_type='application/json')

    httpserver.expect_request('/v2/things/abc').respond_with_handler(handler)

    client = StdlibHttpClient(token='hook_token', min_delay_between_retries=timedelta(milliseconds=1))
    response = client.call(method='GET', url=httpserver.url_for('/v2/things/abc'))

    assert response.status_code == 200
    assert response.json() == {'data': {'id': 'abc'}}
    assert auth_headers == ['Bearer hook_token'] * 3


def test_hooks_only_client_raises_api_error_without_retry(httpserver: HTTPServer) -> None:
    """A non-retryable error status reaches the caller as `ApifyApiError` after a single attempt."""
    request_count = 0

    def handler(_request: Request) -> Response:
        nonlocal request_count
        request_count += 1
        return Response(
            response='{"error": {"type": "record-not-found", "message": "Not there."}}',
            status=404,
            content_type='application/json',
        )

    httpserver.expect_request('/v2/things/missing').respond_with_handler(handler)

    client = StdlibHttpClient(token='hook_token')
    with pytest.raises(ApifyApiError) as exc_info:
        client.call(method='GET', url=httpserver.url_for('/v2/things/missing'))

    assert exc_info.value.status_code == 404
    assert request_count == 1


async def test_hooks_only_client_async_retries_and_sends_default_headers(httpserver: HTTPServer) -> None:
    """The async shared `call` gives a `send_request`-only client header merging and 5xx retries too."""
    auth_headers: list[str | None] = []

    def handler(request: Request) -> Response:
        auth_headers.append(request.headers.get('Authorization'))
        if len(auth_headers) < 3:
            return Response(
                response='{"error": {"type": "internal-error", "message": "Server exploded."}}',
                status=500,
                content_type='application/json',
            )
        return Response(response='{"data": {"id": "abc"}}', status=200, content_type='application/json')

    httpserver.expect_request('/v2/things/abc').respond_with_handler(handler)

    client = StdlibHttpClientAsync(token='hook_token', min_delay_between_retries=timedelta(milliseconds=1))
    response = await client.call(method='GET', url=httpserver.url_for('/v2/things/abc'))

    assert response.status_code == 200
    assert response.json() == {'data': {'id': 'abc'}}
    assert auth_headers == ['Bearer hook_token'] * 3


async def test_hooks_only_client_async_raises_api_error_without_retry(httpserver: HTTPServer) -> None:
    """The async pipeline raises `ApifyApiError` without retrying a non-retryable status."""
    request_count = 0

    def handler(_request: Request) -> Response:
        nonlocal request_count
        request_count += 1
        return Response(
            response='{"error": {"type": "record-not-found", "message": "Not there."}}',
            status=404,
            content_type='application/json',
        )

    httpserver.expect_request('/v2/things/missing').respond_with_handler(handler)

    client = StdlibHttpClientAsync(token='hook_token')
    with pytest.raises(ApifyApiError) as exc_info:
        await client.call(method='GET', url=httpserver.url_for('/v2/things/missing'))

    assert exc_info.value.status_code == 404
    assert request_count == 1


def test_hooks_only_client_does_not_retry_an_unclassified_transport_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """The default `is_retryable_transport_error` classifies nothing, so a transport failure ends the call at once."""
    client = StdlibHttpClient(token='hook_token', min_delay_between_retries=timedelta(milliseconds=1))
    send_request = Mock(side_effect=OSError('connection reset'))
    monkeypatch.setattr(client, 'send_request', send_request)

    with pytest.raises(OSError, match='connection reset'):
        client.call(method='GET', url='https://example.com')

    send_request.assert_called_once()


async def test_hooks_only_client_async_does_not_retry_an_unclassified_transport_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The asynchronous pipeline gives up on the first transport failure the client does not classify either."""
    client = StdlibHttpClientAsync(token='hook_token', min_delay_between_retries=timedelta(milliseconds=1))
    send_request = AsyncMock(side_effect=OSError('connection reset'))
    monkeypatch.setattr(client, 'send_request', send_request)

    with pytest.raises(OSError, match='connection reset'):
        await client.call(method='GET', url='https://example.com')

    send_request.assert_awaited_once()
