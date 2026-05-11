"""Unified tests for webhook dispatch (sync + async)."""

from __future__ import annotations

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
