from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from apify_client import ApifyClientAsync


@pytest.mark.asyncio
async def test_store_list(apify_client_async: ApifyClientAsync) -> None:
    """Test listing public actors in the store."""
    actors_list = await apify_client_async.store().list(limit=10)
    assert actors_list is not None
    assert actors_list.items is not None
    assert len(actors_list.items) > 0  # Store always has actors


@pytest.mark.asyncio
async def test_store_list_with_search(apify_client_async: ApifyClientAsync) -> None:
    """Test listing store with search filter."""
    store_page = await apify_client_async.store().list(limit=5, search='web scraper')

    assert store_page is not None
    assert store_page.items is not None
    assert isinstance(store_page.items, list)


@pytest.mark.asyncio
async def test_store_list_pagination(apify_client_async: ApifyClientAsync) -> None:
    """Test store listing pagination."""
    page1 = await apify_client_async.store().list(limit=5, offset=0)
    page2 = await apify_client_async.store().list(limit=5, offset=5)

    assert page1 is not None
    assert page2 is not None
    # Verify different results (if enough actors exist)
    if len(page1.items) == 5 and len(page2.items) > 0:
        assert page1.items[0].id != page2.items[0].id
