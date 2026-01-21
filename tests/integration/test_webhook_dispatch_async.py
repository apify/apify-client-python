from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from apify_client import ApifyClientAsync


@pytest.mark.asyncio
async def test_webhook_dispatch_list(apify_client_async: ApifyClientAsync) -> None:
    """Test listing webhook dispatches."""
    dispatches_page = await apify_client_async.webhook_dispatches().list(limit=10)

    assert dispatches_page is not None
    assert dispatches_page.items is not None
    assert isinstance(dispatches_page.items, list)
    # User may have 0 dispatches, so we just verify the structure
