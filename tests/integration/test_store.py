"""Unified tests for store (sync + async)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ._utils import maybe_await
from apify_client._models import ListOfStoreActors

if TYPE_CHECKING:
    from apify_client import ApifyClient, ApifyClientAsync


async def test_store_list(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing public Actors in the store."""
    actors_list = await maybe_await(client.store().list(limit=10))
    assert isinstance(actors_list, ListOfStoreActors)
    assert actors_list.items is not None
    assert len(actors_list.items) > 0  # Store always has actors


async def test_store_list_with_search(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing store with search filter."""
    store_page = await maybe_await(client.store().list(limit=5, search='web scraper'))
    assert isinstance(store_page, ListOfStoreActors)
    assert store_page.items is not None
    assert isinstance(store_page.items, list)


async def test_store_list_pagination(client: ApifyClient | ApifyClientAsync) -> None:
    """Test store listing pagination."""
    page1 = await maybe_await(client.store().list(limit=5, offset=0))
    page2 = await maybe_await(client.store().list(limit=5, offset=5))
    assert isinstance(page1, ListOfStoreActors)
    assert isinstance(page2, ListOfStoreActors)
    # Verify different results (if enough actors exist)
    if len(page1.items) == 5 and len(page2.items) > 0:
        assert page1.items[0].id != page2.items[0].id
