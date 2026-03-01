from __future__ import annotations

import json
import os
import sys
from importlib import metadata
from typing import TYPE_CHECKING

from werkzeug import Request, Response

from apify_client._http_clients import ImpitHttpClient, ImpitHttpClientAsync

if TYPE_CHECKING:
    from pytest_httpserver import HTTPServer


def _parse_accept_encoding(header: str) -> set[str]:
    """Parse Accept-Encoding header into a set of encoding names, ignoring order and whitespace."""
    return {enc.strip() for enc in header.split(',')}


def _header_handler(request: Request) -> Response:
    return Response(
        status=200,
        headers={},
        response=json.dumps({'received_headers': dict(request.headers)}),
    )


def _get_user_agent() -> str:
    is_at_home = 'APIFY_IS_AT_HOME' in os.environ
    python_version = '.'.join([str(x) for x in sys.version_info[:3]])
    client_version = metadata.version('apify-client')
    return f'ApifyClient/{client_version} ({sys.platform}; Python/{python_version}); isAtHome/{is_at_home}'


async def test_default_headers_async(httpserver: HTTPServer) -> None:
    """Test that default headers are sent with each request."""
    client = ImpitHttpClientAsync(token='placeholder_token')
    httpserver.expect_request('/').respond_with_handler(_header_handler)
    api_url = httpserver.url_for('/').removesuffix('/')

    response = await client.call(method='GET', url=f'{api_url}/')

    request_headers = json.loads(response.text)['received_headers']

    expected_headers = {
        'User-Agent': _get_user_agent(),
        'Accept': 'application/json, */*',
        'Authorization': 'Bearer placeholder_token',
        'Host': f'{httpserver.host}:{httpserver.port}',
    }
    assert {k: v for k, v in request_headers.items() if k != 'Accept-Encoding'} == expected_headers
    assert _parse_accept_encoding(request_headers['Accept-Encoding']) == {'gzip', 'br', 'zstd', 'deflate'}


def test_default_headers_sync(httpserver: HTTPServer) -> None:
    """Test that default headers are sent with each request."""
    client = ImpitHttpClient(token='placeholder_token')
    httpserver.expect_request('/').respond_with_handler(_header_handler)
    api_url = httpserver.url_for('/').removesuffix('/')

    response = client.call(method='GET', url=f'{api_url}/')

    request_headers = json.loads(response.text)['received_headers']

    expected_headers = {
        'User-Agent': _get_user_agent(),
        'Accept': 'application/json, */*',
        'Authorization': 'Bearer placeholder_token',
        'Host': f'{httpserver.host}:{httpserver.port}',
    }
    assert {k: v for k, v in request_headers.items() if k != 'Accept-Encoding'} == expected_headers
    assert _parse_accept_encoding(request_headers['Accept-Encoding']) == {'gzip', 'br', 'zstd', 'deflate'}


async def test_headers_async(httpserver: HTTPServer) -> None:
    """Test that custom headers are sent with each request."""
    client = ImpitHttpClientAsync(
        token='placeholder_token',
        headers={'Test-Header': 'blah', 'User-Agent': 'CustomUserAgent/1.0', 'Authorization': 'strange_value'},
    )
    httpserver.expect_request('/').respond_with_handler(_header_handler)
    api_url = httpserver.url_for('/').removesuffix('/')

    response = await client.call(method='GET', url=f'{api_url}/')

    request_headers = json.loads(response.text)['received_headers']

    expected_headers = {
        'Test-Header': 'blah',
        'User-Agent': 'CustomUserAgent/1.0',
        'Accept': 'application/json, */*',
        'Authorization': 'strange_value',
        'Host': f'{httpserver.host}:{httpserver.port}',
    }
    assert {k: v for k, v in request_headers.items() if k != 'Accept-Encoding'} == expected_headers
    assert _parse_accept_encoding(request_headers['Accept-Encoding']) == {'gzip', 'br', 'zstd', 'deflate'}


def test_headers_sync(httpserver: HTTPServer) -> None:
    """Test that custom headers are sent with each request."""
    client = ImpitHttpClient(
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

    expected_headers = {
        'Test-Header': 'blah',
        'User-Agent': 'CustomUserAgent/1.0',
        'Accept': 'application/json, */*',
        'Authorization': 'strange_value',
        'Host': f'{httpserver.host}:{httpserver.port}',
    }
    assert {k: v for k, v in request_headers.items() if k != 'Accept-Encoding'} == expected_headers
    assert _parse_accept_encoding(request_headers['Accept-Encoding']) == {'gzip', 'br', 'zstd', 'deflate'}
