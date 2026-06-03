"""Unified tests for webhook dispatch (sync + async)."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from typing import TYPE_CHECKING

from ._utils import maybe_await
from apify_client._models import ListOfWebhookDispatches, WebhookDispatch

if TYPE_CHECKING:
    from apify_client import ApifyClient, ApifyClientAsync


async def test_webhook_dispatch_list(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing webhook dispatches."""
    dispatches_page = await maybe_await(client.webhook_dispatches().list(limit=10))
    assert isinstance(dispatches_page, ListOfWebhookDispatches)
    assert dispatches_page.items is not None
    assert isinstance(dispatches_page.items, list)
    # User may have 0 dispatches, so we just verify the structure


async def test_webhook_dispatch_get(client: ApifyClient | ApifyClientAsync) -> None:
    """Test getting a specific webhook dispatch."""
    # First list dispatches to get a dispatch ID
    dispatches_page = await maybe_await(client.webhook_dispatches().list(limit=1))
    assert isinstance(dispatches_page, ListOfWebhookDispatches)

    if dispatches_page.items:
        # If there are dispatches, test the get method
        dispatch_id = dispatches_page.items[0].id
        dispatch = await maybe_await(client.webhook_dispatch(dispatch_id).get())
        assert isinstance(dispatch, WebhookDispatch)
        assert dispatch.id == dispatch_id
    else:
        # If no dispatches, test that get returns None for non-existent ID
        dispatch = await maybe_await(client.webhook_dispatch('non-existent-id').get())
        assert dispatch is None


async def test_webhook_dispatch_collection_iterate(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test paginated iteration over the user's webhook dispatches."""
    iterator = client.webhook_dispatches().iterate(limit=5)
    collected: list[WebhookDispatch] = []
    if is_async:
        assert isinstance(iterator, AsyncIterator)
        async for d in iterator:
            assert isinstance(d, WebhookDispatch)
            collected.append(d)
    else:
        assert isinstance(iterator, Iterator)
        for d in iterator:
            assert isinstance(d, WebhookDispatch)
            collected.append(d)

    assert len(collected) <= 5
    for dispatch in collected:
        assert dispatch.id is not None


async def test_webhook_dispatch_list_pagination(client: ApifyClient | ApifyClientAsync) -> None:
    """Test webhook_dispatches().list() with pagination parameters."""
    page = await maybe_await(client.webhook_dispatches().list(limit=5, offset=0, desc=True))
    assert isinstance(page, ListOfWebhookDispatches)
    assert isinstance(page.items, list)
    # `limit=5` must cap the page size.
    assert len(page.items) <= 5
    # `desc=True` must return dispatches in non-increasing `created_at` order.
    created_ats = [d.created_at for d in page.items if d.created_at is not None]
    assert created_ats == sorted(created_ats, reverse=True)
    # `offset` must move the window — the second page must not start with the same id as the first.
    # Use ascending order so dispatches created by parallel tests can't shift the pages between calls.
    asc_page = await maybe_await(client.webhook_dispatches().list(limit=5, offset=0, desc=False))
    assert isinstance(asc_page, ListOfWebhookDispatches)
    # Only meaningful when the first page is full.
    if len(asc_page.items) == 5:
        next_page = await maybe_await(client.webhook_dispatches().list(limit=5, offset=5, desc=False))
        assert isinstance(next_page, ListOfWebhookDispatches)
        if next_page.items:
            assert asc_page.items[0].id != next_page.items[0].id
