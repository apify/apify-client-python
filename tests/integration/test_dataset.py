"""Unified tests for dataset (sync + async)."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator, Iterator
from contextlib import AbstractAsyncContextManager, AbstractContextManager
from datetime import timedelta
from typing import TYPE_CHECKING

import impit
import pytest

from ._utils import (
    DatasetFixture,
    collect_iterate_until_present,
    get_random_resource_name,
    maybe_await,
    maybe_sleep,
)
from apify_client._models import Dataset, DatasetListItem, DatasetStatistics, ListOfDatasets
from apify_client._resource_clients.dataset import DatasetItemsPage
from apify_client.errors import ApifyApiError

if TYPE_CHECKING:
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
        iterator = dataset.iterate_items()
        if is_async:
            assert isinstance(iterator, AsyncIterator)
            async for _ in iterator:
                pass
        else:
            assert isinstance(iterator, Iterator)
            for _ in iterator:
                pass

    # Dataset content retrieved with correct signature
    signature = test_dataset_of_another_user.signature
    iterator = dataset.iterate_items(signature=signature)
    collected_items: list[dict] = []
    if is_async:
        assert isinstance(iterator, AsyncIterator)
        async for item in iterator:
            assert isinstance(item, dict)
            collected_items.append(item)
    else:
        assert isinstance(iterator, Iterator)
        for item in iterator:
            assert isinstance(item, dict)
            collected_items.append(item)
    assert test_dataset_of_another_user.expected_content == collected_items


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
        iterator = dataset_client.iterate_items()
        collected_items: list[dict] = []
        if is_async:
            assert isinstance(iterator, AsyncIterator)
            async for item in iterator:
                assert isinstance(item, dict)
                collected_items.append(item)
        else:
            assert isinstance(iterator, Iterator)
            for item in iterator:
                assert isinstance(item, dict)
                collected_items.append(item)

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
        assert isinstance(statistics, DatasetStatistics)

    finally:
        await maybe_await(dataset_client.delete())


async def test_dataset_collection_iterate(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test iterating over the user's datasets across pages."""
    created_ids: list[str] = []

    # Create three datasets so pagination has work to do
    for _ in range(3):
        dataset = await maybe_await(client.datasets().get_or_create(name=get_random_resource_name('dataset')))
        assert isinstance(dataset, Dataset)
        created_ids.append(dataset.id)

    try:
        collected = await collect_iterate_until_present(
            lambda: client.datasets().iterate(desc=True),
            set(created_ids),
            item_type=DatasetListItem,
            is_async=is_async,
        )
        collected_ids = {ds.id for ds in collected}
        for created_id in created_ids:
            assert created_id in collected_ids
    finally:
        for ds_id in created_ids:
            await maybe_await(client.dataset(ds_id).delete())


async def test_dataset_list_items_desc(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test listing items in descending order."""
    dataset_name = get_random_resource_name('dataset')
    created_dataset = await maybe_await(client.datasets().get_or_create(name=dataset_name))
    assert isinstance(created_dataset, Dataset)
    dataset_client = client.dataset(created_dataset.id)

    try:
        items_to_push = [{'idx': i} for i in range(5)]
        await maybe_await(dataset_client.push_items(items_to_push))
        await maybe_sleep(1, is_async=is_async)

        # Default ordering - ascending
        page_asc = await maybe_await(dataset_client.list_items())
        assert isinstance(page_asc, DatasetItemsPage)
        # Reversed ordering
        page_desc = await maybe_await(dataset_client.list_items(desc=True))
        assert isinstance(page_desc, DatasetItemsPage)

        assert page_asc.desc is False
        assert page_desc.desc is True
        assert [item['idx'] for item in page_desc.items] == list(reversed([item['idx'] for item in page_asc.items]))
    finally:
        await maybe_await(dataset_client.delete())


async def test_dataset_list_items_omit_and_clean(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test list_items with `omit`, `clean`, `skip_hidden`, and `skip_empty` filters."""
    dataset_name = get_random_resource_name('dataset')
    created_dataset = await maybe_await(client.datasets().get_or_create(name=dataset_name))
    assert isinstance(created_dataset, Dataset)
    dataset_client = client.dataset(created_dataset.id)

    try:
        # Mix of regular, hidden (`#`), and empty items to exercise filters
        items_to_push = [
            {'id': 1, 'name': 'visible', '#secret': 'shh', 'extra': 'X'},
            {},  # empty item - filtered out by skip_empty/clean
            {'id': 2, 'name': 'also visible', '#secret': 'shh', 'extra': 'Y'},
        ]
        await maybe_await(dataset_client.push_items(items_to_push))
        await maybe_sleep(1, is_async=is_async)

        # `omit` should remove the `extra` field
        omit_page = await maybe_await(dataset_client.list_items(omit=['extra']))
        assert isinstance(omit_page, DatasetItemsPage)
        for item in omit_page.items:
            assert 'extra' not in item

        # `clean=True` drops both hidden (`#secret`) and empty items
        clean_page = await maybe_await(dataset_client.list_items(clean=True))
        assert isinstance(clean_page, DatasetItemsPage)
        assert all(item for item in clean_page.items)  # no empties
        for item in clean_page.items:
            assert '#secret' not in item

        # `skip_hidden=True` keeps empties but drops hidden fields
        hidden_page = await maybe_await(dataset_client.list_items(skip_hidden=True))
        assert isinstance(hidden_page, DatasetItemsPage)
        for item in hidden_page.items:
            assert '#secret' not in item

        # `skip_empty=True` drops empty items but keeps hidden fields
        empty_page = await maybe_await(dataset_client.list_items(skip_empty=True))
        assert isinstance(empty_page, DatasetItemsPage)
        non_empty_count = len([i for i in items_to_push if i])
        assert len(empty_page.items) == non_empty_count
    finally:
        await maybe_await(dataset_client.delete())


async def test_dataset_iterate_items_chunked(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test iterate_items with a small chunk_size to force multiple API requests."""
    dataset_name = get_random_resource_name('dataset')
    created_dataset = await maybe_await(client.datasets().get_or_create(name=dataset_name))
    assert isinstance(created_dataset, Dataset)
    dataset_client = client.dataset(created_dataset.id)

    try:
        items_to_push = [{'idx': i} for i in range(12)]
        await maybe_await(dataset_client.push_items(items_to_push))

        # Poll until all items are visible (eventual consistency); 12 items + 3 paginated reads
        # is more demanding than other dataset tests, so a single 1s sleep is not safe.
        for _ in range(5):
            await maybe_sleep(1, is_async=is_async)
            head = await maybe_await(dataset_client.list_items(limit=12))
            assert isinstance(head, DatasetItemsPage)
            if len(head.items) == 12:
                break

        # chunk_size=5 forces 3 underlying pages for 12 items
        iterator = dataset_client.iterate_items(chunk_size=5)
        collected: list[dict] = []
        if is_async:
            assert isinstance(iterator, AsyncIterator)
            async for item in iterator:
                assert isinstance(item, dict)
                collected.append(item)
        else:
            assert isinstance(iterator, Iterator)
            for item in iterator:
                assert isinstance(item, dict)
                collected.append(item)

        assert len(collected) == 12
        # Ordering across multiple paginated reads is not strictly guaranteed mid-flight,
        # so compare by membership / sorted view rather than positional equality.
        assert sorted(item['idx'] for item in collected) == list(range(12))
    finally:
        await maybe_await(dataset_client.delete())


async def test_dataset_iterate_items_with_fields(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test iterate_items with `fields` filter."""
    dataset_name = get_random_resource_name('dataset')
    created_dataset = await maybe_await(client.datasets().get_or_create(name=dataset_name))
    assert isinstance(created_dataset, Dataset)
    dataset_client = client.dataset(created_dataset.id)

    try:
        items_to_push = [{'id': i, 'name': f'item-{i}', 'extra': 'drop-me'} for i in range(3)]
        await maybe_await(dataset_client.push_items(items_to_push))
        await maybe_sleep(1, is_async=is_async)

        iterator = dataset_client.iterate_items(fields=['id', 'name'])
        collected: list[dict] = []
        if is_async:
            assert isinstance(iterator, AsyncIterator)
            async for item in iterator:
                assert isinstance(item, dict)
                collected.append(item)
        else:
            assert isinstance(iterator, Iterator)
            for item in iterator:
                assert isinstance(item, dict)
                collected.append(item)

        assert len(collected) == 3
        for item in collected:
            assert set(item.keys()) == {'id', 'name'}
    finally:
        await maybe_await(dataset_client.delete())


async def test_dataset_create_items_public_url(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test generating a signed public URL for dataset items and fetching from it."""
    dataset_name = get_random_resource_name('dataset')
    created_dataset = await maybe_await(client.datasets().get_or_create(name=dataset_name))
    assert isinstance(created_dataset, Dataset)
    dataset_client = client.dataset(created_dataset.id)

    try:
        items = [{'id': i, 'value': i * 10} for i in range(3)]
        await maybe_await(dataset_client.push_items(items))
        await maybe_sleep(1, is_async=is_async)

        public_url = await maybe_await(dataset_client.create_items_public_url(expires_in=timedelta(minutes=5)))
        assert isinstance(public_url, str)
        assert created_dataset.id in public_url
        assert 'signature=' in public_url

        # Fetch from the signed URL without any auth header - should succeed
        response = impit.get(public_url)
        assert response.status_code == 200
        downloaded = json.loads(response.content)
        assert downloaded == items
    finally:
        await maybe_await(dataset_client.delete())


async def test_dataset_get_items_as_bytes_csv(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test get_items_as_bytes with non-JSON item_format (csv)."""
    dataset_name = get_random_resource_name('dataset')
    created_dataset = await maybe_await(client.datasets().get_or_create(name=dataset_name))
    assert isinstance(created_dataset, Dataset)
    dataset_client = client.dataset(created_dataset.id)

    try:
        items = [{'id': 1, 'name': 'first'}, {'id': 2, 'name': 'second'}]
        await maybe_await(dataset_client.push_items(items))
        await maybe_sleep(1, is_async=is_async)

        raw = await maybe_await(dataset_client.get_items_as_bytes(item_format='csv'))
        assert isinstance(raw, bytes)
        decoded = raw.decode('utf-8')
        # CSV output should contain a header row and the values
        assert 'id' in decoded
        assert 'first' in decoded
        assert 'second' in decoded
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
        stream_ctx = dataset_client.stream_items(item_format='json')
        if is_async:
            assert isinstance(stream_ctx, AbstractAsyncContextManager)
            async with stream_ctx as response:
                assert isinstance(response, impit.Response)
                assert response.status_code == 200
                content = await response.aread()
                items = json.loads(content)
                assert len(items) == 3
                assert items[0]['id'] == 1
        else:
            assert isinstance(stream_ctx, AbstractContextManager)
            with stream_ctx as response:
                assert isinstance(response, impit.Response)
                assert response.status_code == 200
                content = response.read()
                items = json.loads(content)
                assert len(items) == 3
                assert items[0]['id'] == 1

    finally:
        await maybe_await(dataset_client.delete())
