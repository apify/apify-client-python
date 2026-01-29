"""Unified tests for dataset (sync + async)."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator
    from contextlib import AbstractAsyncContextManager, AbstractContextManager

    from impit import Response

    from apify_client import ApifyClient, ApifyClientAsync
    from apify_client._models import Dataset, ListOfDatasets
    from apify_client._resource_clients.dataset import DatasetItemsPage

import json

import impit
import pytest

from .conftest import DatasetFixture, get_random_resource_name, maybe_await, maybe_sleep
from apify_client.errors import ApifyApiError


async def test_dataset_collection_list(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing datasets."""
    result = await maybe_await(client.datasets().list(limit=10))
    datasets_page = cast('ListOfDatasets', result)

    assert datasets_page is not None
    assert datasets_page.items is not None
    assert isinstance(datasets_page.items, list)


async def test_dataset_collection_list_pagination(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing datasets with pagination."""
    result = await maybe_await(client.datasets().list(limit=5, offset=0))
    datasets_page = cast('ListOfDatasets', result)

    assert datasets_page is not None
    assert datasets_page.items is not None
    assert isinstance(datasets_page.items, list)


async def test_dataset_collection_get_or_create(client: ApifyClient | ApifyClientAsync) -> None:
    """Test get_or_create for datasets."""
    unique_name = get_random_resource_name('dataset')

    # Create new dataset
    result = await maybe_await(client.datasets().get_or_create(name=unique_name))
    dataset = cast('Dataset', result)
    assert dataset is not None
    assert dataset.name == unique_name

    # Get same dataset again (should return existing)
    result2 = await maybe_await(client.datasets().get_or_create(name=unique_name))
    same_dataset = cast('Dataset', result2)
    assert same_dataset.id == dataset.id

    # Cleanup
    await maybe_await(client.dataset(dataset.id).delete())


async def test_dataset_should_create_public_items_expiring_url_with_params(
    client: ApifyClient | ApifyClientAsync,
) -> None:
    dataset_name = get_random_resource_name('dataset')
    result = await maybe_await(client.datasets().get_or_create(name=dataset_name))
    created_dataset = cast('Dataset', result)

    dataset = client.dataset(created_dataset.id)
    result = await maybe_await(
        dataset.create_items_public_url(
            expires_in_secs=2000,
            limit=10,
            offset=0,
        )
    )
    items_public_url = cast('str', result)

    assert 'signature=' in items_public_url
    assert 'limit=10' in items_public_url
    assert 'offset=0' in items_public_url

    impit_client = impit.Client()
    response = impit_client.get(items_public_url, timeout=5)
    assert response.status_code == 200

    await maybe_await(dataset.delete())
    result = await maybe_await(client.dataset(created_dataset.id).get())
    assert result is None


async def test_dataset_should_create_public_items_non_expiring_url(
    client: ApifyClient | ApifyClientAsync,
) -> None:
    dataset_name = get_random_resource_name('dataset')
    result = await maybe_await(client.datasets().get_or_create(name=dataset_name))
    created_dataset = cast('Dataset', result)

    dataset = client.dataset(created_dataset.id)
    result = await maybe_await(dataset.create_items_public_url())
    items_public_url = cast('str', result)

    assert 'signature=' in items_public_url

    impit_client = impit.Client()
    response = impit_client.get(items_public_url, timeout=5)
    assert response.status_code == 200

    await maybe_await(dataset.delete())
    result = await maybe_await(client.dataset(created_dataset.id).get())
    assert result is None


async def test_list_items_signature(
    client: ApifyClient | ApifyClientAsync, test_dataset_of_another_user: DatasetFixture
) -> None:
    dataset = client.dataset(dataset_id=test_dataset_of_another_user.id)

    # Permission error without valid signature
    with pytest.raises(
        ApifyApiError,
        match=r"Insufficient permissions for the dataset. Make sure you're passing a "
        r'correct API token and that it has the required permissions.',
    ):
        await maybe_await(dataset.list_items())

    # Dataset content retrieved with correct signature
    signature = test_dataset_of_another_user.signature
    result = await maybe_await(dataset.list_items(signature=signature))
    list_items_result = cast('DatasetItemsPage', result)
    assert test_dataset_of_another_user.expected_content == list_items_result.items


async def test_iterate_items_signature(
    client: ApifyClient | ApifyClientAsync,
    test_dataset_of_another_user: DatasetFixture,
    *,
    is_async: bool,
) -> None:
    dataset = client.dataset(dataset_id=test_dataset_of_another_user.id)

    # Permission error without valid signature
    with pytest.raises(  # noqa: PT012
        ApifyApiError,
        match=r"Insufficient permissions for the dataset. Make sure you're passing a "
        r'correct API token and that it has the required permissions.',
    ):
        if is_async:
            items = [item async for item in cast('AsyncIterator[dict]', dataset.iterate_items())]  # noqa: F841
        else:
            list(cast('Iterator[dict]', dataset.iterate_items()))

    # Dataset content retrieved with correct signature
    signature = test_dataset_of_another_user.signature
    if is_async:
        collected_items = [
            item async for item in cast('AsyncIterator[dict]', dataset.iterate_items(signature=signature))
        ]
        assert test_dataset_of_another_user.expected_content == collected_items
    else:
        assert test_dataset_of_another_user.expected_content == list(
            cast('Iterator[dict]', dataset.iterate_items(signature=signature))
        )


async def test_get_items_as_bytes_signature(
    client: ApifyClient | ApifyClientAsync, test_dataset_of_another_user: DatasetFixture
) -> None:
    dataset = client.dataset(dataset_id=test_dataset_of_another_user.id)

    # Permission error without valid signature
    with pytest.raises(
        ApifyApiError,
        match=r"Insufficient permissions for the dataset. Make sure you're passing a "
        r'correct API token and that it has the required permissions.',
    ):
        await maybe_await(dataset.get_items_as_bytes())

    # Dataset content retrieved with correct signature
    signature = test_dataset_of_another_user.signature
    result = await maybe_await(dataset.get_items_as_bytes(signature=signature))
    raw_data = cast('bytes', result)
    assert test_dataset_of_another_user.expected_content == json.loads(raw_data.decode('utf-8'))


async def test_dataset_get_or_create_and_get(client: ApifyClient | ApifyClientAsync) -> None:
    """Test creating a dataset and retrieving it."""
    dataset_name = get_random_resource_name('dataset')

    # Create dataset
    result = await maybe_await(client.datasets().get_or_create(name=dataset_name))
    created_dataset = cast('Dataset', result)
    assert created_dataset is not None
    assert created_dataset.id is not None
    assert created_dataset.name == dataset_name

    # Get the same dataset
    dataset_client = client.dataset(created_dataset.id)
    result = await maybe_await(dataset_client.get())
    retrieved_dataset = cast('Dataset | None', result)
    assert retrieved_dataset is not None
    assert retrieved_dataset.id == created_dataset.id
    assert retrieved_dataset.name == dataset_name

    # Cleanup
    await maybe_await(dataset_client.delete())


async def test_dataset_update(client: ApifyClient | ApifyClientAsync) -> None:
    """Test updating dataset properties."""
    dataset_name = get_random_resource_name('dataset')
    new_name = get_random_resource_name('dataset-updated')

    result = await maybe_await(client.datasets().get_or_create(name=dataset_name))
    created_dataset = cast('Dataset', result)
    dataset_client = client.dataset(created_dataset.id)

    # Update the name
    result = await maybe_await(dataset_client.update(name=new_name))
    updated_dataset = cast('Dataset', result)
    assert updated_dataset is not None
    assert updated_dataset.name == new_name
    assert updated_dataset.id == created_dataset.id

    # Verify the update persisted
    result = await maybe_await(dataset_client.get())
    retrieved_dataset = cast('Dataset | None', result)
    assert retrieved_dataset is not None
    assert retrieved_dataset.name == new_name

    # Cleanup
    await maybe_await(dataset_client.delete())


async def test_dataset_push_and_list_items(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test pushing items to dataset and listing them."""
    dataset_name = get_random_resource_name('dataset')

    result = await maybe_await(client.datasets().get_or_create(name=dataset_name))
    created_dataset = cast('Dataset', result)
    dataset_client = client.dataset(created_dataset.id)

    # Push some items
    items_to_push = [
        {'id': 1, 'name': 'Item 1', 'value': 100},
        {'id': 2, 'name': 'Item 2', 'value': 200},
        {'id': 3, 'name': 'Item 3', 'value': 300},
    ]
    await maybe_await(dataset_client.push_items(items_to_push))

    # Wait briefly for eventual consistency
    await maybe_sleep(1, is_async=is_async)

    # List items
    result = await maybe_await(dataset_client.list_items())
    items_page = cast('DatasetItemsPage', result)
    assert items_page is not None
    assert len(items_page.items) == 3
    assert items_page.count == 3
    # Note: items_page.total may be 0 immediately after push due to eventual consistency

    # Verify items content
    for i, item in enumerate(items_page.items):
        assert item['id'] == items_to_push[i]['id']
        assert item['name'] == items_to_push[i]['name']
        assert item['value'] == items_to_push[i]['value']

    # Cleanup
    await maybe_await(dataset_client.delete())


async def test_dataset_list_items_with_pagination(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test listing items with pagination parameters."""
    dataset_name = get_random_resource_name('dataset')

    result = await maybe_await(client.datasets().get_or_create(name=dataset_name))
    created_dataset = cast('Dataset', result)
    dataset_client = client.dataset(created_dataset.id)

    # Push more items
    items_to_push = [{'index': i, 'value': i * 10} for i in range(10)]
    await maybe_await(dataset_client.push_items(items_to_push))

    # Wait briefly for eventual consistency
    await maybe_sleep(1, is_async=is_async)

    # List with limit
    result = await maybe_await(dataset_client.list_items(limit=5))
    items_page = cast('DatasetItemsPage', result)
    assert len(items_page.items) == 5
    assert items_page.count == 5
    # Note: items_page.total may be 0 immediately after push due to eventual consistency
    assert items_page.limit == 5

    # List with offset
    result = await maybe_await(dataset_client.list_items(offset=5, limit=5))
    items_page_offset = cast('DatasetItemsPage', result)
    assert len(items_page_offset.items) == 5
    assert items_page_offset.offset == 5
    # Note: items_page.total may be 0 immediately after push due to eventual consistency

    # Verify different items
    assert items_page.items[0]['index'] != items_page_offset.items[0]['index']

    # Cleanup
    await maybe_await(dataset_client.delete())


async def test_dataset_list_items_with_fields(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test listing items with field filtering."""
    dataset_name = get_random_resource_name('dataset')

    result = await maybe_await(client.datasets().get_or_create(name=dataset_name))
    created_dataset = cast('Dataset', result)
    dataset_client = client.dataset(created_dataset.id)

    # Push items with multiple fields
    items_to_push = [
        {'id': 1, 'name': 'Item 1', 'value': 100, 'extra': 'data1'},
        {'id': 2, 'name': 'Item 2', 'value': 200, 'extra': 'data2'},
    ]
    await maybe_await(dataset_client.push_items(items_to_push))

    # Wait briefly for eventual consistency
    await maybe_sleep(1, is_async=is_async)

    # List with fields filter
    result = await maybe_await(dataset_client.list_items(fields=['id', 'name']))
    items_page = cast('DatasetItemsPage', result)
    assert len(items_page.items) == 2

    # Verify only specified fields are returned
    for item in items_page.items:
        assert 'id' in item
        assert 'name' in item
        assert 'value' not in item
        assert 'extra' not in item

    # Cleanup
    await maybe_await(dataset_client.delete())


async def test_dataset_iterate_items(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test iterating over dataset items."""
    dataset_name = get_random_resource_name('dataset')

    result = await maybe_await(client.datasets().get_or_create(name=dataset_name))
    created_dataset = cast('Dataset', result)
    dataset_client = client.dataset(created_dataset.id)

    # Push items
    items_to_push = [{'index': i} for i in range(5)]
    await maybe_await(dataset_client.push_items(items_to_push))

    # Wait briefly for eventual consistency
    await maybe_sleep(1, is_async=is_async)

    # Iterate over items
    if is_async:
        collected_items = [item async for item in cast('AsyncIterator[dict]', dataset_client.iterate_items())]
    else:
        collected_items = list(cast('Iterator[dict]', dataset_client.iterate_items()))

    assert len(collected_items) == 5
    for i, item in enumerate(collected_items):
        assert item['index'] == i

    # Cleanup
    await maybe_await(dataset_client.delete())


async def test_dataset_delete_nonexistent(client: ApifyClient | ApifyClientAsync) -> None:
    """Test that getting a deleted dataset returns None."""
    dataset_name = get_random_resource_name('dataset')

    result = await maybe_await(client.datasets().get_or_create(name=dataset_name))
    created_dataset = cast('Dataset', result)
    dataset_client = client.dataset(created_dataset.id)

    # Delete dataset
    await maybe_await(dataset_client.delete())

    # Verify it's gone
    result = await maybe_await(dataset_client.get())
    retrieved_dataset = cast('Dataset | None', result)
    assert retrieved_dataset is None


async def test_dataset_get_statistics(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test getting dataset statistics."""
    dataset_name = get_random_resource_name('dataset')

    result = await maybe_await(client.datasets().get_or_create(name=dataset_name))
    created_dataset = cast('Dataset', result)
    dataset_client = client.dataset(created_dataset.id)

    try:
        # Push some items first
        items_to_push = [
            {'id': 1, 'name': 'Item 1'},
            {'id': 2, 'name': 'Item 2'},
        ]
        await maybe_await(dataset_client.push_items(items_to_push))

        # Wait briefly for eventual consistency
        await maybe_sleep(1, is_async=is_async)

        # Get statistics
        result = await maybe_await(dataset_client.get_statistics())
        statistics = cast('dict', result)

        # Verify statistics is returned and properly parsed
        assert statistics is not None

    finally:
        await maybe_await(dataset_client.delete())


async def test_dataset_stream_items(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test streaming dataset items."""
    dataset_name = get_random_resource_name('dataset')

    result = await maybe_await(client.datasets().get_or_create(name=dataset_name))
    created_dataset = cast('Dataset', result)
    dataset_client = client.dataset(created_dataset.id)

    try:
        # Push some items
        items_to_push = [
            {'id': 1, 'name': 'Item 1', 'value': 100},
            {'id': 2, 'name': 'Item 2', 'value': 200},
            {'id': 3, 'name': 'Item 3', 'value': 300},
        ]
        await maybe_await(dataset_client.push_items(items_to_push))

        # Wait briefly for eventual consistency
        await maybe_sleep(1, is_async=is_async)

        # Stream items using context manager
        if is_async:
            stream_ctx = cast('AbstractAsyncContextManager[Response]', dataset_client.stream_items(item_format='json'))
            async with stream_ctx as response:
                assert response is not None
                assert response.status_code == 200
                content = await response.aread()
                items = json.loads(content)
                assert len(items) == 3
                assert items[0]['id'] == 1
        else:
            stream_ctx = cast('AbstractContextManager[Response]', dataset_client.stream_items(item_format='json'))
            with stream_ctx as response:
                assert response is not None
                assert response.status_code == 200
                content = response.read()
                items = json.loads(content)
                assert len(items) == 3
                assert items[0]['id'] == 1

    finally:
        await maybe_await(dataset_client.delete())
