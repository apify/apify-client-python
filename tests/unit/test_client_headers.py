from __future__ import annotations

import json
import os
import sys
from importlib import metadata
from typing import TYPE_CHECKING

from werkzeug import Request, Response

from apify_client._http_client import HTTPClient, HTTPClientAsync

if TYPE_CHECKING:
    from pytest_httpserver import HTTPServer


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

    client = HTTPClientAsync(token='placeholder_token')
    httpserver.expect_request('/').respond_with_handler(_header_handler)
    api_url = httpserver.url_for('/').removesuffix('/')

    response = await client.call(method='GET', url=f'{api_url}/')

    request_headers = json.loads(response.text)['received_headers']

    assert request_headers == {
        'User-Agent': _get_user_agent(),
        'Accept': 'application/json, */*',
        'Authorization': 'Bearer placeholder_token',
        'Accept-Encoding': 'gzip, br, zstd, deflate',
        'Host': f'{httpserver.host}:{httpserver.port}',
    }


def test_default_headers_sync(httpserver: HTTPServer) -> None:
    """Test that default headers are sent with each request."""

    client = HTTPClient(token='placeholder_token')
    httpserver.expect_request('/').respond_with_handler(_header_handler)
    api_url = httpserver.url_for('/').removesuffix('/')

    response = client.call(method='GET', url=f'{api_url}/')

    request_headers = json.loads(response.text)['received_headers']

    assert request_headers == {
        'User-Agent': _get_user_agent(),
        'Accept': 'application/json, */*',
        'Authorization': 'Bearer placeholder_token',
        'Accept-Encoding': 'gzip, br, zstd, deflate',
        'Host': f'{httpserver.host}:{httpserver.port}',
    }


async def test_extra_headers_async(httpserver: HTTPServer) -> None:
    """Test that extra headers are sent with each request."""

    extra_headers = {
        'Test-Header': 'blah',
        'User-Agent': 'CustomUserAgent/1.0',  # Do not override Apify User-Agent
    }
    client = HTTPClientAsync(token='placeholder_token', extra_headers=extra_headers)
    httpserver.expect_request('/').respond_with_handler(_header_handler)
    api_url = httpserver.url_for('/').removesuffix('/')

    response = await client.call(method='GET', url=f'{api_url}/')

    request_headers = json.loads(response.text)['received_headers']

    assert request_headers == {
        'Test-Header': 'blah',
        'User-Agent': _get_user_agent(),  # Do not override Apify User-Agent
        'Accept': 'application/json, */*',
        'Authorization': 'Bearer placeholder_token',
        'Accept-Encoding': 'gzip, br, zstd, deflate',
        'Host': f'{httpserver.host}:{httpserver.port}',
    }


def test_extra_headers_sync(httpserver: HTTPServer) -> None:
    """Test that extra headers are sent with each request."""

    extra_headers = {
        'Test-Header': 'blah',
        'User-Agent': 'CustomUserAgent/1.0',  # Do not override Apify User-Agent
    }
    client = HTTPClient(token='placeholder_token', extra_headers=extra_headers)
    httpserver.expect_request('/').respond_with_handler(_header_handler)
    api_url = httpserver.url_for('/').removesuffix('/')

    response = client.call(method='GET', url=f'{api_url}/')

    request_headers = json.loads(response.text)['received_headers']

    assert request_headers == {
        'Test-Header': 'blah',
        'User-Agent': _get_user_agent(),  # Do not override Apify User-Agent
        'Accept': 'application/json, */*',
        'Authorization': 'Bearer placeholder_token',
        'Accept-Encoding': 'gzip, br, zstd, deflate',
        'Host': f'{httpserver.host}:{httpserver.port}',
    }
