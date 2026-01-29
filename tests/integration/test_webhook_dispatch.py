"""Unified tests for webhook dispatch (sync + async)."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from apify_client import ApifyClient, ApifyClientAsync
    from apify_client._models import ListOfWebhookDispatches, WebhookDispatch


from .conftest import maybe_await


async def test_webhook_dispatch_list(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing webhook dispatches."""
    result = await maybe_await(client.webhook_dispatches().list(limit=10))
    dispatches_page = cast('ListOfWebhookDispatches', result)

    assert dispatches_page is not None
    assert dispatches_page.items is not None
    assert isinstance(dispatches_page.items, list)
    # User may have 0 dispatches, so we just verify the structure


async def test_webhook_dispatch_get(client: ApifyClient | ApifyClientAsync) -> None:
    """Test getting a specific webhook dispatch."""
    # First list dispatches to get a dispatch ID
    result = await maybe_await(client.webhook_dispatches().list(limit=1))
    dispatches_page = cast('ListOfWebhookDispatches', result)
    assert dispatches_page is not None

    if dispatches_page.items:
        # If there are dispatches, test the get method
        dispatch_id = dispatches_page.items[0].id
        result = await maybe_await(client.webhook_dispatch(dispatch_id).get())
        dispatch = cast('WebhookDispatch', result)

        assert dispatch is not None
        assert dispatch.id == dispatch_id
    else:
        # If no dispatches, test that get returns None for non-existent ID
        dispatch = await maybe_await(client.webhook_dispatch('non-existent-id').get())
        assert dispatch is None
