from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest
from werkzeug.wrappers import Response

from apify_client import ApifyClient, ApifyClientAsync

if TYPE_CHECKING:
    from collections.abc import Callable

    from pytest_httpserver import HTTPServer
    from werkzeug.wrappers import Request

_MOCK_LIST_RESPONSE = json.dumps(
    {
        'data': {
            'items': [],
            'count': 0,
            'offset': 0,
            'limit': 100,
            'total': 0,
            'desc': False,
        }
    }
)


def _make_handler(captured: dict) -> Callable[[Request], Response]:
    def handler(request: Request) -> Response:
        captured['args'] = dict(request.args)
        return Response(_MOCK_LIST_RESPONSE, content_type='application/json')

    return handler


@pytest.fixture
def client_urls(httpserver: HTTPServer) -> dict:
    server_url = httpserver.url_for('/').removesuffix('/')
    return {'api_url': server_url, 'api_public_url': server_url}


def test_dataset_collection_list_ownership_sync(httpserver: HTTPServer, client_urls: dict) -> None:
    captured: dict = {}
    httpserver.expect_oneshot_request('/v2/datasets', method='GET').respond_with_handler(_make_handler(captured))

    client = ApifyClient(token='placeholder_token', **client_urls)
    result = client.datasets().list(ownership='ownedByMe')

    assert result.total == 0
    assert captured['args']['ownership'] == 'ownedByMe'


async def test_dataset_collection_list_ownership_async(httpserver: HTTPServer, client_urls: dict) -> None:
    captured: dict = {}
    httpserver.expect_oneshot_request('/v2/datasets', method='GET').respond_with_handler(_make_handler(captured))

    client = ApifyClientAsync(token='placeholder_token', **client_urls)
    result = await client.datasets().list(ownership='sharedWithMe')

    assert result.total == 0
    assert captured['args']['ownership'] == 'sharedWithMe'


def test_key_value_store_collection_list_ownership_sync(httpserver: HTTPServer, client_urls: dict) -> None:
    captured: dict = {}
    httpserver.expect_oneshot_request('/v2/key-value-stores', method='GET').respond_with_handler(
        _make_handler(captured)
    )

    client = ApifyClient(token='placeholder_token', **client_urls)
    result = client.key_value_stores().list(ownership='ownedByMe')

    assert result.total == 0
    assert captured['args']['ownership'] == 'ownedByMe'


async def test_key_value_store_collection_list_ownership_async(httpserver: HTTPServer, client_urls: dict) -> None:
    captured: dict = {}
    httpserver.expect_oneshot_request('/v2/key-value-stores', method='GET').respond_with_handler(
        _make_handler(captured)
    )

    client = ApifyClientAsync(token='placeholder_token', **client_urls)
    result = await client.key_value_stores().list(ownership='sharedWithMe')

    assert result.total == 0
    assert captured['args']['ownership'] == 'sharedWithMe'


def test_request_queue_collection_list_ownership_sync(httpserver: HTTPServer, client_urls: dict) -> None:
    captured: dict = {}
    httpserver.expect_oneshot_request('/v2/request-queues', method='GET').respond_with_handler(_make_handler(captured))

    client = ApifyClient(token='placeholder_token', **client_urls)
    result = client.request_queues().list(ownership='ownedByMe')

    assert result.total == 0
    assert captured['args']['ownership'] == 'ownedByMe'


async def test_request_queue_collection_list_ownership_async(httpserver: HTTPServer, client_urls: dict) -> None:
    captured: dict = {}
    httpserver.expect_oneshot_request('/v2/request-queues', method='GET').respond_with_handler(_make_handler(captured))

    client = ApifyClientAsync(token='placeholder_token', **client_urls)
    result = await client.request_queues().list(ownership='sharedWithMe')

    assert result.total == 0
    assert captured['args']['ownership'] == 'sharedWithMe'
