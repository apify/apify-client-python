"""Unified tests for store (sync + async)."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from apify_client import ApifyClient, ApifyClientAsync
    from apify_client._models import ListOfStoreActors


from .conftest import maybe_await


async def test_store_list(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing public Actors in the store."""
    result = await maybe_await(client.store().list(limit=10))
    actors_list = cast('ListOfStoreActors', result)
    assert actors_list is not None
    assert actors_list.items is not None
    assert len(actors_list.items) > 0  # Store always has actors


async def test_store_list_with_search(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing store with search filter."""
    result = await maybe_await(client.store().list(limit=5, search='web scraper'))
    store_page = cast('ListOfStoreActors', result)

    assert store_page is not None
    assert store_page.items is not None
    assert isinstance(store_page.items, list)


async def test_store_list_pagination(client: ApifyClient | ApifyClientAsync) -> None:
    """Test store listing pagination."""
    result1 = await maybe_await(client.store().list(limit=5, offset=0))
    result2 = await maybe_await(client.store().list(limit=5, offset=5))
    page1 = cast('ListOfStoreActors', result1)
    page2 = cast('ListOfStoreActors', result2)

    assert page1 is not None
    assert page2 is not None
    # Verify different results (if enough actors exist)
    if len(page1.items) == 5 and len(page2.items) > 0:
        assert page1.items[0].id != page2.items[0].id
