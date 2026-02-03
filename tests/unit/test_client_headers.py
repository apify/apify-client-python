from __future__ import annotations

import json
import os
import sys
from importlib import metadata
from typing import TYPE_CHECKING

import pytest
from werkzeug import Request, Response

from apify_client import ApifyClient, ApifyClientAsync
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


async def test_headers_async(httpserver: HTTPServer) -> None:
    """Test that custom headers are sent with each request."""

    client = HTTPClientAsync(
        token='placeholder_token',
        headers={'Test-Header': 'blah', 'User-Agent': 'CustomUserAgent/1.0', 'Authorization': 'strange_value'},
    )
    httpserver.expect_request('/').respond_with_handler(_header_handler)
    api_url = httpserver.url_for('/').removesuffix('/')

    response = await client.call(method='GET', url=f'{api_url}/')

    request_headers = json.loads(response.text)['received_headers']

    assert request_headers == {
        'Test-Header': 'blah',
        'User-Agent': 'CustomUserAgent/1.0',
        'Accept': 'application/json, */*',
        'Authorization': 'strange_value',
        'Accept-Encoding': 'gzip, br, zstd, deflate',
        'Host': f'{httpserver.host}:{httpserver.port}',
    }


def test_headers_sync(httpserver: HTTPServer) -> None:
    """Test that custom headers are sent with each request."""

    client = HTTPClient(
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

    assert request_headers == {
        'Test-Header': 'blah',
        'User-Agent': 'CustomUserAgent/1.0',
        'Accept': 'application/json, */*',
        'Authorization': 'strange_value',
        'Accept-Encoding': 'gzip, br, zstd, deflate',
        'Host': f'{httpserver.host}:{httpserver.port}',
    }


def test_warning_on_overridden_headers_sync() -> None:
    """Test that warning is raised when default headers are overridden."""

    with pytest.warns(UserWarning, match='User-Agent, Authorization headers of ApifyClient'):
        ApifyClient(
            token='placeholder_token',
            headers={
                'User-Agent': 'CustomUserAgent/1.0',
                'Authorization': 'strange_value',
            },
        )


async def test_warning_on_overridden_headers_async() -> None:
    """Test that warning is raised when default headers are overridden."""

    with pytest.warns(UserWarning, match='User-Agent, Authorization headers of ApifyClientAsync'):
        ApifyClientAsync(
            token='placeholder_token',
            headers={
                'User-Agent': 'CustomUserAgent/1.0',
                'Authorization': 'strange_value',
            },
        )
