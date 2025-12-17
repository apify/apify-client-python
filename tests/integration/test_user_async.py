from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apify_client import ApifyClientAsync


async def test_get_user(apify_client_async: ApifyClientAsync) -> None:
    """Test getting user information."""
    user = await apify_client_async.user().get()

    assert user is not None
    # UserPublicInfo has username but not id
    assert user.username is not None


async def test_limits(apify_client_async: ApifyClientAsync) -> None:
    """Test getting account limits."""
    limits = await apify_client_async.user().limits()

    assert limits is not None
    # Verify we have at least some limit information
    # The actual fields depend on the account type
