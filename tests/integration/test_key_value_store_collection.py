"""Unified tests for key-value store collection (sync + async)."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from apify_client import ApifyClient, ApifyClientAsync
    from apify_client._models import KeyValueStore, ListOfKeyValueStores

import uuid

from .conftest import maybe_await


async def test_key_value_stores_list(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing key-value stores."""
    result = await maybe_await(client.key_value_stores().list(limit=10))
    kvs_page = cast('ListOfKeyValueStores', result)

    assert kvs_page is not None
    assert kvs_page.items is not None
    assert isinstance(kvs_page.items, list)


async def test_key_value_stores_list_pagination(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing key-value stores with pagination."""
    result = await maybe_await(client.key_value_stores().list(limit=5, offset=0))
    kvs_page = cast('ListOfKeyValueStores', result)

    assert kvs_page is not None
    assert kvs_page.items is not None
    assert isinstance(kvs_page.items, list)


async def test_key_value_stores_get_or_create(client: ApifyClient | ApifyClientAsync) -> None:
    """Test get_or_create for key-value stores."""
    unique_name = f'test-kvs-{uuid.uuid4().hex[:8]}'

    # Create new KVS
    result = await maybe_await(client.key_value_stores().get_or_create(name=unique_name))
    kvs = cast('KeyValueStore', result)
    assert kvs is not None
    assert kvs.name == unique_name

    # Get same KVS again (should return existing)
    result2 = await maybe_await(client.key_value_stores().get_or_create(name=unique_name))
    same_kvs = cast('KeyValueStore', result2)
    assert same_kvs.id == kvs.id

    # Cleanup
    await maybe_await(client.key_value_store(kvs.id).delete())
