from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest
from werkzeug import Request, Response

if TYPE_CHECKING:
    from collections.abc import Callable

    from pytest_httpserver import HTTPServer

    from apify_client import ApifyClient, ApifyClientAsync

pytestmark = pytest.mark.usefixtures('http_client_classes')

_STORE_PATH = '/v2/store'

_STORE_RESPONSE = {
    'data': {
        'total': 0,
        'offset': 0,
        'limit': 1000,
        'desc': False,
        'count': 0,
        'items': [],
    }
}


def capture(captured: list[Request]) -> Callable[[Request], Response]:
    def handler(request: Request) -> Response:
        captured.append(request)
        return Response(json.dumps(_STORE_RESPONSE), status=200, mimetype='application/json')

    return handler


def test_list_sends_include_unrunnable_actors(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """`list` sends `include_unrunnable_actors` as the `includeUnrunnableActors` query parameter."""
    captured: list[Request] = []
    httpserver.expect_request(_STORE_PATH, method='GET').respond_with_handler(capture(captured))

    sync_client.store().list(include_unrunnable_actors=True)

    assert len(captured) == 1
    assert captured[0].args.get('includeUnrunnableActors') == 'true'


async def test_list_sends_include_unrunnable_actors_async(
    httpserver: HTTPServer, async_client: ApifyClientAsync
) -> None:
    """Async `list` sends `include_unrunnable_actors` as the `includeUnrunnableActors` query parameter."""
    captured: list[Request] = []
    httpserver.expect_request(_STORE_PATH, method='GET').respond_with_handler(capture(captured))

    await async_client.store().list(include_unrunnable_actors=True)

    assert len(captured) == 1
    assert captured[0].args.get('includeUnrunnableActors') == 'true'


def test_iterate_sends_include_unrunnable_actors(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """`iterate` forwards `include_unrunnable_actors` to every page request."""
    captured: list[Request] = []
    httpserver.expect_request(_STORE_PATH, method='GET').respond_with_handler(capture(captured))

    list(sync_client.store().iterate(include_unrunnable_actors=True))

    assert len(captured) == 1
    assert captured[0].args.get('includeUnrunnableActors') == 'true'


async def test_iterate_sends_include_unrunnable_actors_async(
    httpserver: HTTPServer, async_client: ApifyClientAsync
) -> None:
    """Async `iterate` forwards `include_unrunnable_actors` to every page request."""
    captured: list[Request] = []
    httpserver.expect_request(_STORE_PATH, method='GET').respond_with_handler(capture(captured))

    actors = [actor async for actor in async_client.store().iterate(include_unrunnable_actors=True)]

    assert actors == []
    assert len(captured) == 1
    assert captured[0].args.get('includeUnrunnableActors') == 'true'
