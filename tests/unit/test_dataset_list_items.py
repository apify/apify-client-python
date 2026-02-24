from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest
from werkzeug import Response

from apify_client import ApifyClient, ApifyClientAsync

if TYPE_CHECKING:
    from collections.abc import Callable

    from pytest_httpserver import HTTPServer

DATASET_ID = 'test-dataset-id'
ITEMS_PATH = f'/v2/datasets/{DATASET_ID}/items'


def _make_list_items_handler(*, desc_header_value: str) -> Callable:
    """Create a handler that returns a list_items response with the given desc header value."""

    def handler(_request: object) -> Response:
        return Response(
            status=200,
            headers={
                'x-apify-pagination-total': '2',
                'x-apify-pagination-offset': '0',
                'x-apify-pagination-count': '2',
                'x-apify-pagination-limit': '999999999999',
                'x-apify-pagination-desc': desc_header_value,
                'content-type': 'application/json',
            },
            response=json.dumps([{'id': 1}, {'id': 2}]),
        )

    return handler


@pytest.mark.parametrize('desc_header_value', ['false', 'False', 'FALSE'])
def test_list_items_desc_false_sync(httpserver: HTTPServer, desc_header_value: str) -> None:
    httpserver.expect_request(ITEMS_PATH).respond_with_handler(
        _make_list_items_handler(desc_header_value=desc_header_value),
    )
    api_url = httpserver.url_for('/').removesuffix('/')

    client = ApifyClient(token='test-token', api_url=api_url)
    result = client.dataset(dataset_id=DATASET_ID).list_items()

    assert result.desc is False


@pytest.mark.parametrize('desc_header_value', ['true', 'True', 'TRUE'])
def test_list_items_desc_true_sync(httpserver: HTTPServer, desc_header_value: str) -> None:
    httpserver.expect_request(ITEMS_PATH).respond_with_handler(
        _make_list_items_handler(desc_header_value=desc_header_value),
    )
    api_url = httpserver.url_for('/').removesuffix('/')

    client = ApifyClient(token='test-token', api_url=api_url)
    result = client.dataset(dataset_id=DATASET_ID).list_items()

    assert result.desc is True


@pytest.mark.parametrize('desc_header_value', ['false', 'False', 'FALSE'])
async def test_list_items_desc_false_async(httpserver: HTTPServer, desc_header_value: str) -> None:
    httpserver.expect_request(ITEMS_PATH).respond_with_handler(
        _make_list_items_handler(desc_header_value=desc_header_value),
    )
    api_url = httpserver.url_for('/').removesuffix('/')

    client = ApifyClientAsync(token='test-token', api_url=api_url)
    result = await client.dataset(dataset_id=DATASET_ID).list_items()

    assert result.desc is False


@pytest.mark.parametrize('desc_header_value', ['true', 'True', 'TRUE'])
async def test_list_items_desc_true_async(httpserver: HTTPServer, desc_header_value: str) -> None:
    httpserver.expect_request(ITEMS_PATH).respond_with_handler(
        _make_list_items_handler(desc_header_value=desc_header_value),
    )
    api_url = httpserver.url_for('/').removesuffix('/')

    client = ApifyClientAsync(token='test-token', api_url=api_url)
    result = await client.dataset(dataset_id=DATASET_ID).list_items()

    assert result.desc is True
