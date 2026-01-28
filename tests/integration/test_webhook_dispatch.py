from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apify_client import ApifyClient


def test_webhook_dispatch_list(apify_client: ApifyClient) -> None:
    """Test listing webhook dispatches."""
    dispatches_page = apify_client.webhook_dispatches().list(limit=10)

    assert dispatches_page is not None
    assert dispatches_page.items is not None
    assert isinstance(dispatches_page.items, list)
    # User may have 0 dispatches, so we just verify the structure


def test_webhook_dispatch_get(apify_client: ApifyClient) -> None:
    """Test getting a specific webhook dispatch."""
    # First list dispatches to get a dispatch ID
    dispatches_page = apify_client.webhook_dispatches().list(limit=1)
    assert dispatches_page is not None

    if dispatches_page.items:
        # If there are dispatches, test the get method
        dispatch_id = dispatches_page.items[0].id
        dispatch = apify_client.webhook_dispatch(dispatch_id).get()

        assert dispatch is not None
        assert dispatch.id == dispatch_id
    else:
        # If no dispatches, test that get returns None for non-existent ID
        dispatch = apify_client.webhook_dispatch('non-existent-id').get()
        assert dispatch is None
