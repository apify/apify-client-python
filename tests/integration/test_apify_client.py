"""Unified tests for apify client (sync + async)."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from apify_client import ApifyClient, ApifyClientAsync
    from apify_client._models import UserPrivateInfo, UserPublicInfo


from .conftest import maybe_await


async def test_apify_client(client: ApifyClient | ApifyClientAsync) -> None:
    """Test basic apify client functionality."""
    user_client = client.user('me')
    result = await maybe_await(user_client.get())
    me = cast('UserPrivateInfo | UserPublicInfo', result)
    assert me.username is not None
