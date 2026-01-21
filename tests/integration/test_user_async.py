from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from apify_client import ApifyClientAsync


@pytest.mark.asyncio
async def test_get_user(apify_client_async: ApifyClientAsync) -> None:
    """Test getting user information."""
    user = await apify_client_async.user().get()

    assert user is not None
    # UserPublicInfo has username but not id
    assert user.username is not None


@pytest.mark.asyncio
async def test_limits(apify_client_async: ApifyClientAsync) -> None:
    """Test getting account limits."""
    limits = await apify_client_async.user().limits()

    assert limits is not None
    # Verify we have at least some limit information
    # The actual fields depend on the account type


@pytest.mark.asyncio
async def test_monthly_usage(apify_client_async: ApifyClientAsync) -> None:
    """Test retrieving monthly usage information."""
    usage = await apify_client_async.user().monthly_usage()

    assert usage is not None
    # Verify expected fields exist
    assert usage.usage_cycle is not None
    assert isinstance(usage.monthly_service_usage, dict)
    assert isinstance(usage.daily_service_usages, list)
