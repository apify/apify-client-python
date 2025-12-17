from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apify_client import ApifyClient


def test_list_webhooks(apify_client: ApifyClient) -> None:
    """Test listing webhooks."""
    webhooks_page = apify_client.webhooks().list(limit=10)

    assert webhooks_page is not None
    assert webhooks_page.items is not None
    # User may have 0 webhooks
    assert isinstance(webhooks_page.items, list)


def test_list_webhooks_pagination(apify_client: ApifyClient) -> None:
    """Test listing webhooks with pagination."""
    webhooks_page = apify_client.webhooks().list(limit=5, offset=0)

    assert webhooks_page is not None
    assert webhooks_page.items is not None
    assert isinstance(webhooks_page.items, list)
