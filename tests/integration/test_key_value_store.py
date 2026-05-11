"""Unified tests for key-value store (sync + async)."""

from __future__ import annotations

import json
from datetime import timedelta
from typing import TYPE_CHECKING, cast

import impit
import pytest

from ._utils import KvsFixture, get_random_resource_name, maybe_await, maybe_sleep
from apify_client._models import KeyValueStore, ListOfKeys, ListOfKeyValueStores
from apify_client.errors import ApifyApiError

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator

    from apify_client import ApifyClient, ApifyClientAsync
    from apify_client._models import KeyValueStoreKey


async def test_key_value_store_collection_list(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing key-value stores."""
    kvs_page = await maybe_await(client.key_value_stores().list(limit=10))
    assert isinstance(kvs_page, ListOfKeyValueStores)
    assert kvs_page.items is not None
    assert isinstance(kvs_page.items, list)


async def test_key_value_store_collection_list_pagination(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing key-value stores with pagination."""
    kvs_page = await maybe_await(client.key_value_stores().list(limit=5, offset=0))
    assert isinstance(kvs_page, ListOfKeyValueStores)
    assert kvs_page.items is not None
    assert isinstance(kvs_page.items, list)


async def test_key_value_store_collection_get_or_create(client: ApifyClient | ApifyClientAsync) -> None:
    """Test get_or_create for key-value stores."""
    unique_name = get_random_resource_name('kvs')

    # Create new KVS
    kvs = await maybe_await(client.key_value_stores().get_or_create(name=unique_name))
    assert isinstance(kvs, KeyValueStore)

    try:
        assert kvs.name == unique_name

        # Get same KVS again (should return existing)
        same_kvs = await maybe_await(client.key_value_stores().get_or_create(name=unique_name))
        assert isinstance(same_kvs, KeyValueStore)
        assert same_kvs.id == kvs.id
    finally:
        await maybe_await(client.key_value_store(kvs.id).delete())


async def test_key_value_store_should_create_expiring_keys_public_url_with_params(
    client: ApifyClient | ApifyClientAsync,
) -> None:
    store_name = get_random_resource_name('key-value-store')
    created_store = await maybe_await(client.key_value_stores().get_or_create(name=store_name))
    assert isinstance(created_store, KeyValueStore)

    store = client.key_value_store(created_store.id)

    try:
        keys_public_url = await maybe_await(
            store.create_keys_public_url(
                expires_in=timedelta(seconds=2000),
                limit=10,
            )
        )
        assert isinstance(keys_public_url, str)
        assert 'signature=' in keys_public_url
        assert 'limit=10' in keys_public_url

        impit_client = impit.Client()
        response = impit_client.get(keys_public_url, timeout=30)
        assert response.status_code == 200
    finally:
        await maybe_await(store.delete())


async def test_key_value_store_should_create_public_keys_non_expiring_url(
    client: ApifyClient | ApifyClientAsync,
) -> None:
    store_name = get_random_resource_name('key-value-store')
    created_store = await maybe_await(client.key_value_stores().get_or_create(name=store_name))
    assert isinstance(created_store, KeyValueStore)

    store = client.key_value_store(created_store.id)

    try:
        keys_public_url = await maybe_await(store.create_keys_public_url())
        assert isinstance(keys_public_url, str)
        assert 'signature=' in keys_public_url

        impit_client = impit.Client()
        response = impit_client.get(keys_public_url, timeout=30)
        assert response.status_code == 200
    finally:
        await maybe_await(store.delete())


async def test_list_keys_signature(
    client: ApifyClient | ApifyClientAsync, test_kvs_of_another_user: KvsFixture
) -> None:
    kvs = client.key_value_store(key_value_store_id=test_kvs_of_another_user.id)

    # Permission error without valid signature
    with pytest.raises(
        ApifyApiError,
        match=r"Insufficient permissions for the key-value store. Make sure you're passing a correct"
        r' API token and that it has the required permissions.',
    ):
        await maybe_await(kvs.list_keys())

    # Kvs content retrieved with correct signature
    response = await maybe_await(kvs.list_keys(signature=test_kvs_of_another_user.signature))
    assert isinstance(response, ListOfKeys)
    raw_items = response.items

    assert set(test_kvs_of_another_user.expected_content) == {item.key for item in raw_items}


async def test_get_record_signature(
    client: ApifyClient | ApifyClientAsync, test_kvs_of_another_user: KvsFixture
) -> None:
    key = 'key1'
    kvs = client.key_value_store(key_value_store_id=test_kvs_of_another_user.id)

    # Permission error without valid signature
    with pytest.raises(
        ApifyApiError,
        match=r"Insufficient permissions for the key-value store. Make sure you're passing a correct"
        r' API token and that it has the required permissions.',
    ):
        await maybe_await(kvs.get_record(key))

    # Kvs content retrieved with correct signature
    record = await maybe_await(kvs.get_record(key, signature=test_kvs_of_another_user.keys_signature[key]))
    assert isinstance(record, dict)
    assert test_kvs_of_another_user.expected_content[key] == record['value']


async def test_get_record_as_bytes_signature(
    client: ApifyClient | ApifyClientAsync, test_kvs_of_another_user: KvsFixture
) -> None:
    key = 'key1'
    kvs = client.key_value_store(key_value_store_id=test_kvs_of_another_user.id)

    # Permission error without valid signature
    with pytest.raises(
        ApifyApiError,
        match=r"Insufficient permissions for the key-value store. Make sure you're passing a correct"
        r' API token and that it has the required permissions.',
    ):
        await maybe_await(kvs.get_record_as_bytes(key))

    # Kvs content retrieved with correct signature
    item = await maybe_await(kvs.get_record_as_bytes(key, signature=test_kvs_of_another_user.keys_signature[key]))
    assert isinstance(item, dict)
    assert test_kvs_of_another_user.expected_content[key] == json.loads(item['value'].decode('utf-8'))


async def test_stream_record_signature(
    client: ApifyClient | ApifyClientAsync,
    test_kvs_of_another_user: KvsFixture,
    *,
    is_async: bool,
) -> None:
    key = 'key1'
    kvs = client.key_value_store(key_value_store_id=test_kvs_of_another_user.id)

    # Permission error without valid signature
    # Note: stream_record returns a context manager, so we need to handle it differently
    # For sync/async unification, we can't use 'with await maybe_await(...)' directly
    # We'll test the error condition separately based on client type
    if is_async:
        with pytest.raises(ApifyApiError):
            async with kvs.stream_record(key) as stream:  # ty: ignore[invalid-context-manager]
                pass
    else:
        with pytest.raises(ApifyApiError), kvs.stream_record(key) as stream:  # ty: ignore[invalid-context-manager]
            pass

    # Kvs content retrieved with correct signature
    if is_async:
        async with kvs.stream_record(
            key,
            signature=test_kvs_of_another_user.keys_signature[key],
        ) as stream:  # ty: ignore[invalid-context-manager]
            assert isinstance(stream, dict)
            value = json.loads(stream['value'].content.decode('utf-8'))
    else:
        with kvs.stream_record(
            key,
            signature=test_kvs_of_another_user.keys_signature[key],
        ) as stream:  # ty: ignore[invalid-context-manager]
            assert isinstance(stream, dict)
            value = json.loads(stream['value'].content.decode('utf-8'))

    assert test_kvs_of_another_user.expected_content[key] == value


async def test_key_value_store_get_or_create_and_get(client: ApifyClient | ApifyClientAsync) -> None:
    """Test creating a key-value store and retrieving it."""
    store_name = get_random_resource_name('kvs')

    # Create store
    created_store = await maybe_await(client.key_value_stores().get_or_create(name=store_name))
    assert isinstance(created_store, KeyValueStore)
    assert created_store.id is not None
    assert created_store.name == store_name

    # Get the same store
    store_client = client.key_value_store(created_store.id)

    try:
        retrieved_store = await maybe_await(store_client.get())
        assert isinstance(retrieved_store, KeyValueStore)
        assert retrieved_store.id == created_store.id
        assert retrieved_store.name == store_name
    finally:
        await maybe_await(store_client.delete())


async def test_key_value_store_update(client: ApifyClient | ApifyClientAsync) -> None:
    """Test updating key-value store properties."""
    store_name = get_random_resource_name('kvs')
    new_name = get_random_resource_name('kvs-updated')

    created_store = await maybe_await(client.key_value_stores().get_or_create(name=store_name))
    assert isinstance(created_store, KeyValueStore)
    store_client = client.key_value_store(created_store.id)

    try:
        # Update the name
        updated_store = await maybe_await(store_client.update(name=new_name))
        assert isinstance(updated_store, KeyValueStore)
        assert updated_store.name == new_name
        assert updated_store.id == created_store.id

        # Verify the update persisted
        retrieved_store = await maybe_await(store_client.get())
        assert isinstance(retrieved_store, KeyValueStore)
        assert retrieved_store.name == new_name
    finally:
        await maybe_await(store_client.delete())


async def test_key_value_store_set_and_get_record(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test setting and getting records from key-value store."""
    store_name = get_random_resource_name('kvs')

    created_store = await maybe_await(client.key_value_stores().get_or_create(name=store_name))
    assert isinstance(created_store, KeyValueStore)
    store_client = client.key_value_store(created_store.id)

    try:
        # Set a JSON record
        test_value = {'name': 'Test Item', 'value': 123, 'nested': {'data': 'value'}}
        await maybe_await(store_client.set_record('test-key', test_value))

        # Wait briefly for eventual consistency
        await maybe_sleep(1, is_async=is_async)

        # Get the record
        record = await maybe_await(store_client.get_record('test-key'))
        assert isinstance(record, dict)
        assert record['key'] == 'test-key'
        assert record['value'] == test_value
        assert 'application/json' in record['content_type']
    finally:
        await maybe_await(store_client.delete())


async def test_key_value_store_set_and_get_text_record(
    client: ApifyClient | ApifyClientAsync, *, is_async: bool
) -> None:
    """Test setting and getting text records."""
    store_name = get_random_resource_name('kvs')

    created_store = await maybe_await(client.key_value_stores().get_or_create(name=store_name))
    assert isinstance(created_store, KeyValueStore)
    store_client = client.key_value_store(created_store.id)

    try:
        # Set a text record
        test_text = 'Hello, this is a test text!'
        await maybe_await(store_client.set_record('text-key', test_text, content_type='text/plain'))

        # Wait briefly for eventual consistency
        await maybe_sleep(1, is_async=is_async)

        # Get the record
        record = await maybe_await(store_client.get_record('text-key'))
        assert isinstance(record, dict)
        assert record['key'] == 'text-key'
        assert record['value'] == test_text
        assert 'text/plain' in record['content_type']
    finally:
        await maybe_await(store_client.delete())


async def test_key_value_store_list_keys(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test listing keys in the key-value store."""
    store_name = get_random_resource_name('kvs')

    created_store = await maybe_await(client.key_value_stores().get_or_create(name=store_name))
    assert isinstance(created_store, KeyValueStore)
    store_client = client.key_value_store(created_store.id)

    try:
        # Set multiple records
        for i in range(5):
            await maybe_await(store_client.set_record(f'key-{i}', {'index': i}))

        # Wait briefly for eventual consistency
        await maybe_sleep(1, is_async=is_async)

        # List keys
        keys_response = await maybe_await(store_client.list_keys())
        assert isinstance(keys_response, ListOfKeys)
        assert len(keys_response.items) == 5

        # Verify key names
        key_names = [item.key for item in keys_response.items]
        for i in range(5):
            assert f'key-{i}' in key_names
    finally:
        await maybe_await(store_client.delete())


async def test_key_value_store_list_keys_with_limit(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test listing keys with limit parameter."""
    store_name = get_random_resource_name('kvs')

    created_store = await maybe_await(client.key_value_stores().get_or_create(name=store_name))
    assert isinstance(created_store, KeyValueStore)
    store_client = client.key_value_store(created_store.id)

    try:
        # Set multiple records
        for i in range(10):
            await maybe_await(store_client.set_record(f'item-{i:02d}', {'index': i}))

        # Wait briefly for eventual consistency
        await maybe_sleep(1, is_async=is_async)

        # List with limit
        keys_response = await maybe_await(store_client.list_keys(limit=5))
        assert isinstance(keys_response, ListOfKeys)
        assert len(keys_response.items) == 5
    finally:
        await maybe_await(store_client.delete())


async def test_key_value_store_record_exists(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test checking if a record exists."""
    store_name = get_random_resource_name('kvs')

    created_store = await maybe_await(client.key_value_stores().get_or_create(name=store_name))
    assert isinstance(created_store, KeyValueStore)
    store_client = client.key_value_store(created_store.id)

    try:
        # Set a record
        await maybe_await(store_client.set_record('exists-key', {'data': 'value'}))

        # Wait briefly for eventual consistency
        await maybe_sleep(1, is_async=is_async)

        # Check existence
        exists = await maybe_await(store_client.record_exists('exists-key'))
        assert exists is True
        exists = await maybe_await(store_client.record_exists('non-existent-key'))
        assert exists is False
    finally:
        await maybe_await(store_client.delete())


async def test_key_value_store_delete_record(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test deleting a record from the store."""
    store_name = get_random_resource_name('kvs')

    created_store = await maybe_await(client.key_value_stores().get_or_create(name=store_name))
    assert isinstance(created_store, KeyValueStore)
    store_client = client.key_value_store(created_store.id)

    try:
        # Set a record
        await maybe_await(store_client.set_record('delete-me', {'data': 'value'}))

        # Wait briefly for eventual consistency
        await maybe_sleep(1, is_async=is_async)

        # Verify it exists
        record = await maybe_await(store_client.get_record('delete-me'))
        assert record is not None

        # Delete the record
        await maybe_await(store_client.delete_record('delete-me'))

        # Wait briefly
        await maybe_sleep(1, is_async=is_async)

        # Verify it's gone
        record = await maybe_await(store_client.get_record('delete-me'))
        assert record is None
    finally:
        await maybe_await(store_client.delete())


async def test_key_value_store_delete_nonexistent(client: ApifyClient | ApifyClientAsync) -> None:
    """Test that getting a deleted store returns None."""
    store_name = get_random_resource_name('kvs')

    created_store = await maybe_await(client.key_value_stores().get_or_create(name=store_name))
    assert isinstance(created_store, KeyValueStore)
    store_client = client.key_value_store(created_store.id)

    # Delete store
    await maybe_await(store_client.delete())

    # Verify it's gone
    retrieved_store = await maybe_await(store_client.get())
    assert retrieved_store is None


async def test_key_value_store_iterate_keys(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test iterating over keys in the key-value store."""
    store_name = get_random_resource_name('kvs')

    created_store = await maybe_await(client.key_value_stores().get_or_create(name=store_name))
    assert isinstance(created_store, KeyValueStore)
    store_client = client.key_value_store(created_store.id)

    try:
        # Set multiple records
        for i in range(5):
            await maybe_await(store_client.set_record(f'key-{i}', {'index': i}))

        # Wait briefly for eventual consistency
        await maybe_sleep(1, is_async=is_async)

        # Iterate over keys
        if is_async:
            collected_keys = [key async for key in cast('AsyncIterator[KeyValueStoreKey]', store_client.iterate_keys())]
        else:
            collected_keys = list(cast('Iterator[KeyValueStoreKey]', store_client.iterate_keys()))

        assert len(collected_keys) == 5

        # Verify key names
        key_names = [key.key for key in collected_keys]
        for i in range(5):
            assert f'key-{i}' in key_names
    finally:
        await maybe_await(store_client.delete())


async def test_key_value_store_iterate_keys_with_limit(
    client: ApifyClient | ApifyClientAsync, *, is_async: bool
) -> None:
    """Test iterating over keys with limit parameter."""
    store_name = get_random_resource_name('kvs')

    created_store = await maybe_await(client.key_value_stores().get_or_create(name=store_name))
    assert isinstance(created_store, KeyValueStore)
    store_client = client.key_value_store(created_store.id)

    try:
        # Set multiple records
        for i in range(10):
            await maybe_await(store_client.set_record(f'item-{i:02d}', {'index': i}))

        # Wait briefly for eventual consistency
        await maybe_sleep(1, is_async=is_async)

        # Iterate with limit
        if is_async:
            collected_keys = [
                key async for key in cast('AsyncIterator[KeyValueStoreKey]', store_client.iterate_keys(limit=5))
            ]
        else:
            collected_keys = list(cast('Iterator[KeyValueStoreKey]', store_client.iterate_keys(limit=5)))

        assert len(collected_keys) == 5
    finally:
        await maybe_await(store_client.delete())


async def test_key_value_store_iterate_keys_with_prefix(
    client: ApifyClient | ApifyClientAsync, *, is_async: bool
) -> None:
    """Test iterating over keys with prefix filter."""
    store_name = get_random_resource_name('kvs')

    created_store = await maybe_await(client.key_value_stores().get_or_create(name=store_name))
    assert isinstance(created_store, KeyValueStore)
    store_client = client.key_value_store(created_store.id)

    try:
        # Set records with different prefixes
        for i in range(3):
            await maybe_await(store_client.set_record(f'prefix-a-{i}', {'type': 'a', 'index': i}))
        for i in range(2):
            await maybe_await(store_client.set_record(f'prefix-b-{i}', {'type': 'b', 'index': i}))

        # Wait briefly for eventual consistency
        await maybe_sleep(1, is_async=is_async)

        # Iterate with prefix filter
        if is_async:
            collected_keys = [
                key
                async for key in cast('AsyncIterator[KeyValueStoreKey]', store_client.iterate_keys(prefix='prefix-a-'))
            ]
        else:
            collected_keys = list(cast('Iterator[KeyValueStoreKey]', store_client.iterate_keys(prefix='prefix-a-')))

        assert len(collected_keys) == 3
        for key in collected_keys:
            assert key.key.startswith('prefix-a-')
    finally:
        await maybe_await(store_client.delete())
