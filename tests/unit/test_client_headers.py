from __future__ import annotations

import json
import os
import sys
from importlib import metadata
from typing import TYPE_CHECKING

import httpx
from werkzeug import Request, Response

from apify_client.http_clients import HttpxHttpClient, HttpxHttpClientAsync, ImpitHttpClient, ImpitHttpClientAsync

if TYPE_CHECKING:
    from pytest_httpserver import HTTPServer

    from apify_client.http_clients import HttpClient, HttpClientAsync


def _parse_accept_encoding(header: str) -> set[str]:
    """Parse Accept-Encoding header into a set of encoding names, ignoring order and whitespace."""
    return {enc.strip() for enc in header.split(',')}


def _transport_wire_headers(
    client_class: type[HttpClient | HttpClientAsync],
) -> tuple[dict[str, str], set[str]]:
    """Return the headers the transport adds on its own and the content encodings it advertises."""
    if issubclass(client_class, (ImpitHttpClient, ImpitHttpClientAsync)):
        return {}, {'zstd', 'gzip', 'deflate', 'br'}
    # HTTPX advertises whichever decoders happen to be installed alongside it, so read the set off the client
    # itself rather than hard-coding it and breaking whenever the environment gains or loses a codec.
    with httpx.Client() as probe:
        return {'Connection': 'keep-alive'}, _parse_accept_encoding(probe.headers['accept-encoding'])


def _header_handler(request: Request) -> Response:
    return Response(
        status=200,
        headers={},
        response=json.dumps({'received_headers': dict(request.headers)}),
    )


def _get_user_agent() -> str:
    is_at_home = str('APIFY_IS_AT_HOME' in os.environ).lower()
    python_version = '.'.join([str(x) for x in sys.version_info[:3]])
    client_version = metadata.version('apify-client')
    return f'ApifyClient/{client_version} ({sys.platform}; Python/{python_version}); isAtHome/{is_at_home}'


async def test_default_headers_async(httpserver: HTTPServer, http_client_async_class: type[HttpClientAsync]) -> None:
    """Test that default headers are sent with each request."""
    client = http_client_async_class(token='placeholder_token')
    httpserver.expect_request('/').respond_with_handler(_header_handler)
    api_url = httpserver.url_for('/').removesuffix('/')

    response = await client.call(method='GET', url=f'{api_url}/')

    request_headers = json.loads(response.text)['received_headers']
    transport_headers, expected_encodings = _transport_wire_headers(http_client_async_class)

    expected_headers = {
        'User-Agent': _get_user_agent(),
        'Accept': 'application/json, */*',
        'Authorization': 'Bearer placeholder_token',
        'Host': f'{httpserver.host}:{httpserver.port}',
        **transport_headers,
    }
    assert {k: v for k, v in request_headers.items() if k != 'Accept-Encoding'} == expected_headers
    assert _parse_accept_encoding(request_headers['Accept-Encoding']) == expected_encodings


def test_default_headers_sync(httpserver: HTTPServer, http_client_class: type[HttpClient]) -> None:
    """Test that default headers are sent with each request."""
    client = http_client_class(token='placeholder_token')
    httpserver.expect_request('/').respond_with_handler(_header_handler)
    api_url = httpserver.url_for('/').removesuffix('/')

    response = client.call(method='GET', url=f'{api_url}/')

    request_headers = json.loads(response.text)['received_headers']
    transport_headers, expected_encodings = _transport_wire_headers(http_client_class)

    expected_headers = {
        'User-Agent': _get_user_agent(),
        'Accept': 'application/json, */*',
        'Authorization': 'Bearer placeholder_token',
        'Host': f'{httpserver.host}:{httpserver.port}',
        **transport_headers,
    }
    assert {k: v for k, v in request_headers.items() if k != 'Accept-Encoding'} == expected_headers
    assert _parse_accept_encoding(request_headers['Accept-Encoding']) == expected_encodings


async def test_headers_async(httpserver: HTTPServer, http_client_async_class: type[HttpClientAsync]) -> None:
    """Test that custom headers are sent with each request."""
    client = http_client_async_class(
        token='placeholder_token',
        headers={'Test-Header': 'blah', 'User-Agent': 'CustomUserAgent/1.0', 'Authorization': 'strange_value'},
    )
    httpserver.expect_request('/').respond_with_handler(_header_handler)
    api_url = httpserver.url_for('/').removesuffix('/')

    response = await client.call(method='GET', url=f'{api_url}/')

    request_headers = json.loads(response.text)['received_headers']
    transport_headers, expected_encodings = _transport_wire_headers(http_client_async_class)

    expected_headers = {
        'Test-Header': 'blah',
        'User-Agent': 'CustomUserAgent/1.0',
        'Accept': 'application/json, */*',
        'Authorization': 'strange_value',
        'Host': f'{httpserver.host}:{httpserver.port}',
        **transport_headers,
    }
    assert {k: v for k, v in request_headers.items() if k != 'Accept-Encoding'} == expected_headers
    assert _parse_accept_encoding(request_headers['Accept-Encoding']) == expected_encodings


def test_headers_sync(httpserver: HTTPServer, http_client_class: type[HttpClient]) -> None:
    """Test that custom headers are sent with each request."""
    client = http_client_class(
        token='placeholder_token',
        headers={
            'Test-Header': 'blah',
            'User-Agent': 'CustomUserAgent/1.0',
            'Authorization': 'strange_value',
        },
    )
    httpserver.expect_request('/').respond_with_handler(_header_handler)
    api_url = httpserver.url_for('/').removesuffix('/')

    response = client.call(method='GET', url=f'{api_url}/')

    request_headers = json.loads(response.text)['received_headers']
    transport_headers, expected_encodings = _transport_wire_headers(http_client_class)

    expected_headers = {
        'Test-Header': 'blah',
        'User-Agent': 'CustomUserAgent/1.0',
        'Accept': 'application/json, */*',
        'Authorization': 'strange_value',
        'Host': f'{httpserver.host}:{httpserver.port}',
        **transport_headers,
    }
    assert {k: v for k, v in request_headers.items() if k != 'Accept-Encoding'} == expected_headers
    assert _parse_accept_encoding(request_headers['Accept-Encoding']) == expected_encodings


async def test_per_request_headers_override_defaults_async(
    httpserver: HTTPServer, http_client_async_class: type[HttpClientAsync]
) -> None:
    """Test that a per-request header overrides a same-named default header on the wire, without duplication."""
    client = http_client_async_class(token='placeholder_token')
    httpserver.expect_request('/').respond_with_handler(_header_handler)
    api_url = httpserver.url_for('/').removesuffix('/')

    response = await client.call(method='GET', url=f'{api_url}/', headers={'authorization': 'Bearer per-request'})

    request_headers = json.loads(response.text)['received_headers']

    # WSGI joins duplicate headers into one comma-separated value, so exact equality
    # also proves the authorization header was sent only once.
    assert request_headers['Authorization'] == 'Bearer per-request'


def test_per_request_headers_override_defaults_sync(
    httpserver: HTTPServer, http_client_class: type[HttpClient]
) -> None:
    """Test that a per-request header overrides a same-named default header on the wire, without duplication."""
    client = http_client_class(token='placeholder_token')
    httpserver.expect_request('/').respond_with_handler(_header_handler)
    api_url = httpserver.url_for('/').removesuffix('/')

    response = client.call(method='GET', url=f'{api_url}/', headers={'authorization': 'Bearer per-request'})

    request_headers = json.loads(response.text)['received_headers']

    # WSGI joins duplicate headers into one comma-separated value, so exact equality
    # also proves the authorization header was sent only once.
    assert request_headers['Authorization'] == 'Bearer per-request'


def _echo_cookie_handler(request: Request) -> Response:
    return Response(json.dumps({'cookie': request.headers.get('Cookie')}), content_type='application/json')


def test_httpx_does_not_reuse_server_cookies(httpserver: HTTPServer) -> None:
    """A Set-Cookie response must not silently leak into a later API request through HTTPX's shared cookie jar."""
    httpserver.expect_request('/set-cookie').respond_with_data('ok', headers={'Set-Cookie': 'session=secret'})
    httpserver.expect_request('/echo-cookie').respond_with_handler(_echo_cookie_handler)

    with HttpxHttpClient() as client:
        client.call(method='GET', url=httpserver.url_for('/set-cookie'))
        response = client.call(method='GET', url=httpserver.url_for('/echo-cookie'))

    assert response.json() == {'cookie': None}


async def test_httpx_async_does_not_reuse_server_cookies(httpserver: HTTPServer) -> None:
    """The asynchronous HTTPX pool also remains stateless between API calls."""
    httpserver.expect_request('/set-cookie').respond_with_data('ok', headers={'Set-Cookie': 'session=secret'})
    httpserver.expect_request('/echo-cookie').respond_with_handler(_echo_cookie_handler)

    async with HttpxHttpClientAsync() as client:
        await client.call(method='GET', url=httpserver.url_for('/set-cookie'))
        response = await client.call(method='GET', url=httpserver.url_for('/echo-cookie'))

    assert response.json() == {'cookie': None}


def test_httpx_keeps_explicit_cookie_header(httpserver: HTTPServer) -> None:
    """Disabling the shared cookie jar must not remove a Cookie header explicitly supplied by the caller."""
    httpserver.expect_request('/echo-explicit-cookie').respond_with_handler(_echo_cookie_handler)

    with HttpxHttpClient() as client:
        response = client.call(
            method='GET',
            url=httpserver.url_for('/echo-explicit-cookie'),
            headers={'Cookie': 'explicit=value'},
        )

    assert response.json() == {'cookie': 'explicit=value'}
