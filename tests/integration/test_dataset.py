"""Unified tests for dataset (sync + async)."""

from __future__ import annotations

import json
from datetime import timedelta
from typing import TYPE_CHECKING, cast

import impit
import pytest

from ._utils import DatasetFixture, get_random_resource_name, maybe_await, maybe_sleep
from apify_client._models import Dataset, ListOfDatasets
from apify_client._resource_clients.dataset import DatasetItemsPage
from apify_client.errors import ApifyApiError

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator
    from contextlib import AbstractAsyncContextManager, AbstractContextManager

    from impit import Response

    from apify_client import ApifyClient, ApifyClientAsync


async def test_dataset_collection_list(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing datasets."""
    datasets_page = await maybe_await(client.datasets().list(limit=10))
    assert isinstance(datasets_page, ListOfDatasets)
    assert datasets_page.items is not None
    assert isinstance(datasets_page.items, list)


async def test_dataset_collection_list_pagination(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing datasets with pagination."""
    datasets_page = await maybe_await(client.datasets().list(limit=5, offset=0))
    assert isinstance(datasets_page, ListOfDatasets)
    assert datasets_page.items is not None
    assert isinstance(datasets_page.items, list)


async def test_dataset_collection_get_or_create(client: ApifyClient | ApifyClientAsync) -> None:
    """Test get_or_create for datasets."""
    unique_name = get_random_resource_name('dataset')

    # Create new dataset
    dataset = await maybe_await(client.datasets().get_or_create(name=unique_name))
    assert isinstance(dataset, Dataset)

    try:
        assert dataset.name == unique_name

        # Get same dataset again (should return existing)
        same_dataset = await maybe_await(client.datasets().get_or_create(name=unique_name))
        assert isinstance(same_dataset, Dataset)
        assert same_dataset.id == dataset.id
    finally:
        await maybe_await(client.dataset(dataset.id).delete())


async def test_dataset_should_create_public_items_expiring_url_with_params(
    client: ApifyClient | ApifyClientAsync,
) -> None:
    dataset_name = get_random_resource_name('dataset')
    created_dataset = await maybe_await(client.datasets().get_or_create(name=dataset_name))
    assert isinstance(created_dataset, Dataset)

    dataset = client.dataset(created_dataset.id)

    try:
        items_public_url = await maybe_await(
            dataset.create_items_public_url(
                expires_in=timedelta(seconds=2000),
                limit=10,
                offset=0,
            )
        )
        assert isinstance(items_public_url, str)
        assert 'signature=' in items_public_url
        assert 'limit=10' in items_public_url
        assert 'offset=0' in items_public_url

        impit_client = impit.Client()
        response = impit_client.get(items_public_url, timeout=30)
        assert response.status_code == 200
    finally:
        await maybe_await(dataset.delete())


async def test_dataset_should_create_public_items_non_expiring_url(
    client: ApifyClient | ApifyClientAsync,
) -> None:
    dataset_name = get_random_resource_name('dataset')
    created_dataset = await maybe_await(client.datasets().get_or_create(name=dataset_name))
    assert isinstance(created_dataset, Dataset)

    dataset = client.dataset(created_dataset.id)

    try:
        items_public_url = await maybe_await(dataset.create_items_public_url())
        assert isinstance(items_public_url, str)
        assert 'signature=' in items_public_url

        impit_client = impit.Client()
        response = impit_client.get(items_public_url, timeout=30)
        assert response.status_code == 200
    finally:
        await maybe_await(dataset.delete())


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
    list_items_result = await maybe_await(dataset.list_items(signature=signature))
    assert isinstance(list_items_result, DatasetItemsPage)
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
            async for _ in cast('AsyncIterator[dict]', dataset.iterate_items()):
                pass
        else:
            for _ in cast('Iterator[dict]', dataset.iterate_items()):
                pass

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
    raw_data = await maybe_await(dataset.get_items_as_bytes(signature=signature))
    assert isinstance(raw_data, bytes)
    assert test_dataset_of_another_user.expected_content == json.loads(raw_data.decode('utf-8'))


async def test_dataset_get_or_create_and_get(client: ApifyClient | ApifyClientAsync) -> None:
    """Test creating a dataset and retrieving it."""
    dataset_name = get_random_resource_name('dataset')

    # Create dataset
    created_dataset = await maybe_await(client.datasets().get_or_create(name=dataset_name))
    assert isinstance(created_dataset, Dataset)
    assert created_dataset.id is not None
    assert created_dataset.name == dataset_name

    # Get the same dataset
    dataset_client = client.dataset(created_dataset.id)

    try:
        retrieved_dataset = await maybe_await(dataset_client.get())
        assert isinstance(retrieved_dataset, Dataset)
        assert retrieved_dataset.id == created_dataset.id
        assert retrieved_dataset.name == dataset_name
    finally:
        await maybe_await(dataset_client.delete())


async def test_dataset_update(client: ApifyClient | ApifyClientAsync) -> None:
    """Test updating dataset properties."""
    dataset_name = get_random_resource_name('dataset')
    new_name = get_random_resource_name('dataset-updated')

    created_dataset = await maybe_await(client.datasets().get_or_create(name=dataset_name))
    assert isinstance(created_dataset, Dataset)
    dataset_client = client.dataset(created_dataset.id)

    try:
        # Update the name
        updated_dataset = await maybe_await(dataset_client.update(name=new_name))
        assert isinstance(updated_dataset, Dataset)
        assert updated_dataset.name == new_name
        assert updated_dataset.id == created_dataset.id

        # Verify the update persisted
        retrieved_dataset = await maybe_await(dataset_client.get())
        assert isinstance(retrieved_dataset, Dataset)
        assert retrieved_dataset.name == new_name
    finally:
        await maybe_await(dataset_client.delete())


async def test_dataset_push_and_list_items(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test pushing items to dataset and listing them."""
    dataset_name = get_random_resource_name('dataset')

    created_dataset = await maybe_await(client.datasets().get_or_create(name=dataset_name))
    assert isinstance(created_dataset, Dataset)
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

        # List items
        items_page = await maybe_await(dataset_client.list_items())
        assert isinstance(items_page, DatasetItemsPage)
        assert len(items_page.items) == 3
        assert items_page.count == 3
        # Note: items_page.total may be 0 immediately after push due to eventual consistency

        # Verify items content
        for i, item in enumerate(items_page.items):
            assert item['id'] == items_to_push[i]['id']
            assert item['name'] == items_to_push[i]['name']
            assert item['value'] == items_to_push[i]['value']
    finally:
        await maybe_await(dataset_client.delete())


async def test_dataset_list_items_with_pagination(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test listing items with pagination parameters."""
    dataset_name = get_random_resource_name('dataset')

    created_dataset = await maybe_await(client.datasets().get_or_create(name=dataset_name))
    assert isinstance(created_dataset, Dataset)
    dataset_client = client.dataset(created_dataset.id)

    try:
        # Push more items
        items_to_push = [{'index': i, 'value': i * 10} for i in range(10)]
        await maybe_await(dataset_client.push_items(items_to_push))

        # Wait briefly for eventual consistency
        await maybe_sleep(1, is_async=is_async)

        # List with limit
        items_page = await maybe_await(dataset_client.list_items(limit=5))
        assert isinstance(items_page, DatasetItemsPage)
        assert len(items_page.items) == 5
        assert items_page.count == 5
        # Note: items_page.total may be 0 immediately after push due to eventual consistency
        assert items_page.limit == 5

        # List with offset
        items_page_offset = await maybe_await(dataset_client.list_items(offset=5, limit=5))
        assert isinstance(items_page_offset, DatasetItemsPage)
        assert len(items_page_offset.items) == 5
        assert items_page_offset.offset == 5
        # Note: items_page.total may be 0 immediately after push due to eventual consistency

        # Verify different items
        assert items_page.items[0]['index'] != items_page_offset.items[0]['index']
    finally:
        await maybe_await(dataset_client.delete())


async def test_dataset_list_items_with_fields(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test listing items with field filtering."""
    dataset_name = get_random_resource_name('dataset')

    created_dataset = await maybe_await(client.datasets().get_or_create(name=dataset_name))
    assert isinstance(created_dataset, Dataset)
    dataset_client = client.dataset(created_dataset.id)

    try:
        # Push items with multiple fields
        items_to_push = [
            {'id': 1, 'name': 'Item 1', 'value': 100, 'extra': 'data1'},
            {'id': 2, 'name': 'Item 2', 'value': 200, 'extra': 'data2'},
        ]
        await maybe_await(dataset_client.push_items(items_to_push))

        # Wait briefly for eventual consistency
        await maybe_sleep(1, is_async=is_async)

        # List with fields filter
        items_page = await maybe_await(dataset_client.list_items(fields=['id', 'name']))
        assert isinstance(items_page, DatasetItemsPage)
        assert len(items_page.items) == 2

        # Verify only specified fields are returned
        for item in items_page.items:
            assert 'id' in item
            assert 'name' in item
            assert 'value' not in item
            assert 'extra' not in item
    finally:
        await maybe_await(dataset_client.delete())


async def test_dataset_iterate_items(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test iterating over dataset items."""
    dataset_name = get_random_resource_name('dataset')

    created_dataset = await maybe_await(client.datasets().get_or_create(name=dataset_name))
    assert isinstance(created_dataset, Dataset)
    dataset_client = client.dataset(created_dataset.id)

    try:
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
    finally:
        await maybe_await(dataset_client.delete())


async def test_dataset_delete_nonexistent(client: ApifyClient | ApifyClientAsync) -> None:
    """Test that getting a deleted dataset returns None."""
    dataset_name = get_random_resource_name('dataset')

    created_dataset = await maybe_await(client.datasets().get_or_create(name=dataset_name))
    assert isinstance(created_dataset, Dataset)
    dataset_client = client.dataset(created_dataset.id)

    # Delete dataset
    await maybe_await(dataset_client.delete())

    # Verify it's gone
    retrieved_dataset = await maybe_await(dataset_client.get())
    assert retrieved_dataset is None


async def test_dataset_get_statistics(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test getting dataset statistics."""
    dataset_name = get_random_resource_name('dataset')

    created_dataset = await maybe_await(client.datasets().get_or_create(name=dataset_name))
    assert isinstance(created_dataset, Dataset)
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
        statistics = await maybe_await(dataset_client.get_statistics())

        # Verify statistics is returned and properly parsed
        assert isinstance(statistics, dict)

    finally:
        await maybe_await(dataset_client.delete())


async def test_dataset_stream_items(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test streaming dataset items."""
    dataset_name = get_random_resource_name('dataset')

    created_dataset = await maybe_await(client.datasets().get_or_create(name=dataset_name))
    assert isinstance(created_dataset, Dataset)
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
