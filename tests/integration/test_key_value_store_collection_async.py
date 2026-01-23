from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apify_client import ApifyClientAsync


async def test_key_value_stores_list(apify_client_async: ApifyClientAsync) -> None:
    """Test listing key-value stores."""
    kvs_page = await apify_client_async.key_value_stores().list(limit=10)

    assert kvs_page is not None
    assert kvs_page.items is not None
    assert isinstance(kvs_page.items, list)


async def test_key_value_stores_list_pagination(apify_client_async: ApifyClientAsync) -> None:
    """Test listing key-value stores with pagination."""
    kvs_page = await apify_client_async.key_value_stores().list(limit=5, offset=0)

    assert kvs_page is not None
    assert kvs_page.items is not None
    assert isinstance(kvs_page.items, list)


async def test_key_value_stores_get_or_create(apify_client_async: ApifyClientAsync) -> None:
    """Test get_or_create for key-value stores."""
    unique_name = f'test-kvs-{uuid.uuid4().hex[:8]}'

    # Create new KVS
    kvs = await apify_client_async.key_value_stores().get_or_create(name=unique_name)
    assert kvs is not None
    assert kvs.name == unique_name

    # Get same KVS again (should return existing)
    same_kvs = await apify_client_async.key_value_stores().get_or_create(name=unique_name)
    assert same_kvs.id == kvs.id

    # Cleanup
    await apify_client_async.key_value_store(kvs.id).delete()
