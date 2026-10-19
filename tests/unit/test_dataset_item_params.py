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

_DATASET_ID = 'test-dataset-id'
_ITEMS_PATH = f'/v2/datasets/{_DATASET_ID}/items'


def capture(captured: list[Request]) -> Callable[[Request], Response]:
    def handler(request: Request) -> Response:
        captured.append(request)
        return Response(
            status=200,
            headers={
                'x-apify-pagination-total': '1',
                'x-apify-pagination-offset': '0',
                'x-apify-pagination-count': '1',
                'x-apify-pagination-limit': '999999999999',
                'x-apify-pagination-desc': 'false',
                'content-type': 'application/json',
            },
            response=json.dumps([{'id': 1}]),
        )

    return handler


def test_iterate_items_sends_flatten_and_view(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """`iterate_items` forwards `flatten` and `view` to the page requests."""
    captured: list[Request] = []
    httpserver.expect_request(_ITEMS_PATH, method='GET').respond_with_handler(capture(captured))

    items = list(sync_client.dataset(_DATASET_ID).iterate_items(limit=1, flatten=['a', 'b'], view='overview'))

    assert items == [{'id': 1}]
    assert captured[0].args.get('flatten') == 'a,b'
    assert captured[0].args.get('view') == 'overview'


async def test_iterate_items_sends_flatten_and_view_async(
    httpserver: HTTPServer, async_client: ApifyClientAsync
) -> None:
    """Async `iterate_items` forwards `flatten` and `view` to the page requests."""
    captured: list[Request] = []
    httpserver.expect_request(_ITEMS_PATH, method='GET').respond_with_handler(capture(captured))

    dataset = async_client.dataset(_DATASET_ID)
    items = [item async for item in dataset.iterate_items(limit=1, flatten=['a', 'b'], view='overview')]

    assert items == [{'id': 1}]
    assert captured[0].args.get('flatten') == 'a,b'
    assert captured[0].args.get('view') == 'overview'


def test_get_items_as_bytes_sends_view_and_attachment(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """`get_items_as_bytes` sends `view` and `attachment` as query parameters."""
    captured: list[Request] = []
    httpserver.expect_request(_ITEMS_PATH, method='GET').respond_with_handler(capture(captured))

    sync_client.dataset(_DATASET_ID).get_items_as_bytes(view='overview', attachment=True)

    assert len(captured) == 1
    assert captured[0].args.get('view') == 'overview'
    assert captured[0].args.get('attachment') == 'true'


async def test_get_items_as_bytes_sends_view_and_attachment_async(
    httpserver: HTTPServer, async_client: ApifyClientAsync
) -> None:
    """Async `get_items_as_bytes` sends `view` and `attachment` as query parameters."""
    captured: list[Request] = []
    httpserver.expect_request(_ITEMS_PATH, method='GET').respond_with_handler(capture(captured))

    await async_client.dataset(_DATASET_ID).get_items_as_bytes(view='overview', attachment=True)

    assert len(captured) == 1
    assert captured[0].args.get('view') == 'overview'
    assert captured[0].args.get('attachment') == 'true'


def test_stream_items_sends_view_and_attachment(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """`stream_items` sends `view` and `attachment` as query parameters."""
    captured: list[Request] = []
    httpserver.expect_request(_ITEMS_PATH, method='GET').respond_with_handler(capture(captured))

    with sync_client.dataset(_DATASET_ID).stream_items(view='overview', attachment=True):
        pass

    assert len(captured) == 1
    assert captured[0].args.get('view') == 'overview'
    assert captured[0].args.get('attachment') == 'true'


async def test_stream_items_sends_view_and_attachment_async(
    httpserver: HTTPServer, async_client: ApifyClientAsync
) -> None:
    """Async `stream_items` sends `view` and `attachment` as query parameters."""
    captured: list[Request] = []
    httpserver.expect_request(_ITEMS_PATH, method='GET').respond_with_handler(capture(captured))

    async with async_client.dataset(_DATASET_ID).stream_items(view='overview', attachment=True):
        pass

    assert len(captured) == 1
    assert captured[0].args.get('view') == 'overview'
    assert captured[0].args.get('attachment') == 'true'
