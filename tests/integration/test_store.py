"""Unified tests for store (sync + async)."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from typing import TYPE_CHECKING

import pytest

from .._utils import maybe_await
from apify_client._models import ListOfStoreActors, StoreListActor

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


@pytest.mark.parametrize('pricing_model', ['FREE', 'FLAT_PRICE_PER_MONTH', 'PRICE_PER_DATASET_ITEM', 'PAY_PER_EVENT'])
async def test_store_list_filter_by_pricing_model(client: ApifyClient | ApifyClientAsync, pricing_model: str) -> None:
    """Test listing store actors filtered by each supported pricing model.

    This exercises both the filter parameter and the Pydantic models that parse the responses for each
    pricing variant.
    """
    page = await maybe_await(client.store().list(limit=10, pricing_model=pricing_model))
    assert isinstance(page, ListOfStoreActors)
    assert isinstance(page.items, list)

    for actor in page.items:
        # current_pricing_info is optional; when present its pricing_model must match the filter
        cp = getattr(actor, 'current_pricing_info', None)
        if cp is not None and hasattr(cp, 'pricing_model'):
            assert cp.pricing_model == pricing_model


async def test_store_list_filter_by_username(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing store actors filtered by a known username (apify)."""
    page = await maybe_await(client.store().list(limit=10, username='apify'))
    assert isinstance(page, ListOfStoreActors)
    assert len(page.items) > 0
    for actor in page.items:
        assert actor.username == 'apify'


async def test_store_list_sort_by_popularity(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing store actors sorted by popularity (a known API-supported sort field)."""
    page = await maybe_await(client.store().list(limit=10, sort_by='popularity'))
    assert isinstance(page, ListOfStoreActors)
    assert len(page.items) > 0
    # `popularity` is a composite ranking, not a strict sort on any single field, so we only
    # check the directional invariant: the top-ranked item has at least as many total users as
    # the bottom-ranked one on the page.
    total_users = [a.stats.total_users for a in page.items if a.stats.total_users is not None]
    assert total_users, 'expected at least one item with populated stats.total_users'
    assert total_users[0] >= total_users[-1]


async def test_store_iterate(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test paginated iteration over store Actors."""
    iterator = client.store().iterate(limit=20)
    collected: list[StoreListActor] = []
    if is_async:
        assert isinstance(iterator, AsyncIterator)
        async for a in iterator:
            assert isinstance(a, StoreListActor)
            collected.append(a)
    else:
        assert isinstance(iterator, Iterator)
        for a in iterator:
            assert isinstance(a, StoreListActor)
            collected.append(a)

    assert len(collected) > 0
    assert len(collected) <= 20
    seen_ids = set()
    for actor in collected:
        assert actor.id is not None
        # IDs should be unique across pages
        assert actor.id not in seen_ids
        seen_ids.add(actor.id)


async def test_store_iterate_filter_by_username(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test paginated iteration with a username filter applied."""
    iterator = client.store().iterate(limit=15, username='apify')
    collected: list[StoreListActor] = []
    if is_async:
        assert isinstance(iterator, AsyncIterator)
        async for a in iterator:
            assert isinstance(a, StoreListActor)
            collected.append(a)
    else:
        assert isinstance(iterator, Iterator)
        for a in iterator:
            assert isinstance(a, StoreListActor)
            collected.append(a)

    assert len(collected) > 0
    for actor in collected:
        assert actor.username == 'apify'


async def test_store_list_parses_full_first_page(client: ApifyClient | ApifyClientAsync) -> None:
    """Test that store.list() parses every item on a 100-actor first page."""
    page = await maybe_await(client.store().list(limit=100))
    assert isinstance(page, ListOfStoreActors)
    # All items have already been validated by Pydantic via `model_validate`. Touch a few
    # fields to make the assertion concrete and to ensure the page wasn't empty.
    assert page.items, f'{type(page).__name__} returned an empty items list — unexpected for the public store'
    for item in page.items:
        assert item.id
        assert item.name
        assert item.username
