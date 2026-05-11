"""Unified tests for apify client (sync + async)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ._utils import maybe_await
from apify_client._models import UserPrivateInfo, UserPublicInfo

if TYPE_CHECKING:
    from apify_client import ApifyClient, ApifyClientAsync


async def test_apify_client(client: ApifyClient | ApifyClientAsync) -> None:
    """Test basic apify client functionality."""
    user_client = client.user('me')
    me = await maybe_await(user_client.get())
    assert isinstance(me, UserPrivateInfo | UserPublicInfo)
    assert me.username is not None
