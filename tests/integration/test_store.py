"""Unified tests for store (sync + async)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from apify_client._models_generated import StoreListActor
from apify_client._pagination_classes import PaginatedPage

if TYPE_CHECKING:
    from apify_client import ApifyClient, ApifyClientAsync


from ._utils import maybe_await


async def test_store_list(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing public Actors in the store."""
    actors_list = await maybe_await(client.store().list(limit=10))

    assert isinstance(actors_list, PaginatedPage)
    assert isinstance(actors_list.items, list)
    assert isinstance(actors_list.items[0], StoreListActor)  # Store always has actors


async def test_store_list_with_search(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing store with search filter."""
    store_page = await maybe_await(client.store().list(limit=5, search='web scraper'))

    assert isinstance(store_page, PaginatedPage)
    assert isinstance(store_page.items, list)
    if store_page.items:
        assert isinstance(store_page.items[0], StoreListActor)


async def test_store_list_pagination(client: ApifyClient | ApifyClientAsync) -> None:
    """Test store listing pagination."""
    page1 = await maybe_await(client.store().list(limit=5, offset=0))
    page2 = await maybe_await(client.store().list(limit=5, offset=5))

    assert isinstance(page1, PaginatedPage)
    assert isinstance(page1.items, list)
    assert isinstance(page1.items[0], StoreListActor)
    assert isinstance(page2, PaginatedPage)
    assert isinstance(page2.items, list)
    # Verify different results (if enough actors exist)
    if len(page1.items) == 5 and len(page2.items) > 0:
        assert isinstance(page2.items[0], StoreListActor)
        assert page1.items[0].id != page2.items[0].id
