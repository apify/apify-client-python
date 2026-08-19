from __future__ import annotations

from typing import TYPE_CHECKING

from apify_client import ApifyClient, ApifyClientAsync
from apify_client.http_clients import HttpResponse

if TYPE_CHECKING:
    from typing import Any

    from pytest_httpserver import HTTPServer

    from apify_client.http_clients import HttpClient, HttpClientAsync


DATASET_ID = 'test-dataset-id'
KVS_ID = 'test-kvs-id'
RECORD_KEY = 'test-record-key'
STREAM_CONTENT = b'[{"id": 1}]'


def test_dataset_stream_items_sync(
    httpserver: HTTPServer,
    http_client_class: type[HttpClient],
) -> None:
    """Dataset streams expose a transport-independent response that can be read synchronously."""
    httpserver.expect_request(f'/v2/datasets/{DATASET_ID}/items').respond_with_data(STREAM_CONTENT)
    api_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClient.with_custom_http_client(
        api_url=api_url,
        http_client=http_client_class(),
    )

    with client.dataset(DATASET_ID).stream_items(item_format='json') as response:
        assert isinstance(response, HttpResponse)
        assert response.read() == STREAM_CONTENT


async def test_dataset_stream_items_async(
    httpserver: HTTPServer,
    http_client_async_class: type[HttpClientAsync],
) -> None:
    """Dataset streams expose a transport-independent response that can be read asynchronously."""
    httpserver.expect_request(f'/v2/datasets/{DATASET_ID}/items').respond_with_data(STREAM_CONTENT)
    api_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClientAsync.with_custom_http_client(
        api_url=api_url,
        http_client=http_client_async_class(),
    )

    async with client.dataset(DATASET_ID).stream_items(item_format='json') as response:
        assert isinstance(response, HttpResponse)
        assert await response.aread() == STREAM_CONTENT


def test_key_value_store_stream_record_sync(
    httpserver: HTTPServer,
    http_client_class: type[HttpClient],
) -> None:
    """KVS streams require reading the generic response before consuming its content."""
    httpserver.expect_request(f'/v2/key-value-stores/{KVS_ID}/records/{RECORD_KEY}').respond_with_data(STREAM_CONTENT)
    api_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClient.with_custom_http_client(
        api_url=api_url,
        http_client=http_client_class(),
    )

    with client.key_value_store(KVS_ID).stream_record(RECORD_KEY) as record:
        assert isinstance(record, dict)
        response = record['value']
        assert isinstance(response, HttpResponse)
        assert response.read() == STREAM_CONTENT


async def test_key_value_store_stream_record_async(
    httpserver: HTTPServer,
    http_client_async_class: type[HttpClientAsync],
) -> None:
    """KVS streams require asynchronously reading the generic response before consuming its content."""
    httpserver.expect_request(f'/v2/key-value-stores/{KVS_ID}/records/{RECORD_KEY}').respond_with_data(STREAM_CONTENT)
    api_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClientAsync.with_custom_http_client(
        api_url=api_url,
        http_client=http_client_async_class(),
    )

    async with client.key_value_store(KVS_ID).stream_record(RECORD_KEY) as record:
        assert isinstance(record, dict)
        response = record['value']
        assert isinstance(response, HttpResponse)
        assert await response.aread() == STREAM_CONTENT


def test_protocol_check_leaves_stream_unread_sync(
    httpserver: HTTPServer,
    http_client_class: type[HttpClient],
) -> None:
    """Checking a streaming response against the protocol inspects it without pulling the body off the wire."""
    httpserver.expect_request(f'/v2/datasets/{DATASET_ID}/items').respond_with_data(STREAM_CONTENT)
    api_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClient.with_custom_http_client(
        api_url=api_url,
        http_client=http_client_class(),
    )

    with client.dataset(DATASET_ID).stream_items(item_format='json') as response:
        assert isinstance(response, HttpResponse)
        # `is_stream_consumed` is transport state, not part of the protocol, but the built-in client exposes it.
        raw: Any = response
        assert raw.is_stream_consumed is False


async def test_protocol_check_leaves_stream_unread_async(
    httpserver: HTTPServer,
    http_client_async_class: type[HttpClientAsync],
) -> None:
    """Checking a streaming response against the protocol inspects it without pulling the body off the wire."""
    httpserver.expect_request(f'/v2/datasets/{DATASET_ID}/items').respond_with_data(STREAM_CONTENT)
    api_url = httpserver.url_for('/').removesuffix('/')
    client = ApifyClientAsync.with_custom_http_client(
        api_url=api_url,
        http_client=http_client_async_class(),
    )

    async with client.dataset(DATASET_ID).stream_items(item_format='json') as response:
        assert isinstance(response, HttpResponse)
        # `is_stream_consumed` is transport state, not part of the protocol, but the built-in client exposes it.
        raw: Any = response
        assert raw.is_stream_consumed is False
