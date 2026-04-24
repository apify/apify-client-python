"""Unified tests for webhook dispatch (sync + async)."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from apify_client._iterable_list_page import ListPage
from apify_client._models_generated import WebhookDispatch

if TYPE_CHECKING:
    from apify_client import ApifyClient, ApifyClientAsync


from ._utils import maybe_await


async def test_webhook_dispatch_list(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing webhook dispatches."""
    dispatches_page = await maybe_await(client.webhook_dispatches().list(limit=10))

    assert isinstance(dispatches_page, ListPage)
    assert isinstance(dispatches_page.items, list)
    # User may have 0 dispatches — only check element type when any were returned.
    if dispatches_page.items:
        assert isinstance(dispatches_page.items[0], WebhookDispatch)


async def test_webhook_dispatch_get(client: ApifyClient | ApifyClientAsync) -> None:
    """Test getting a specific webhook dispatch."""
    # First list dispatches to get a dispatch ID
    dispatches_page = await maybe_await(client.webhook_dispatches().list(limit=1))

    assert isinstance(dispatches_page, ListPage)
    assert isinstance(dispatches_page.items, list)

    if dispatches_page.items:
        # If there are dispatches, test the get method
        assert isinstance(dispatches_page.items[0], WebhookDispatch)
        dispatch_id = dispatches_page.items[0].id
        result = await maybe_await(client.webhook_dispatch(dispatch_id).get())
        dispatch = cast('WebhookDispatch', result)

        assert dispatch is not None
        assert dispatch.id == dispatch_id
    else:
        # If no dispatches, test that get returns None for non-existent ID
        dispatch = await maybe_await(client.webhook_dispatch('non-existent-id').get())
        assert dispatch is None
