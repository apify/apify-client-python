from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apify_client import ApifyClient


def test_get_user(apify_client: ApifyClient) -> None:
    """Test getting user information."""
    user = apify_client.user().get()

    assert user is not None
    # UserPublicInfo has username but not id
    assert user.username is not None


def test_limits(apify_client: ApifyClient) -> None:
    """Test getting account limits."""
    limits = apify_client.user().limits()

    assert limits is not None
    # Verify we have at least some limit information
    # The actual fields depend on the account type


def test_monthly_usage(apify_client: ApifyClient) -> None:
    """Test retrieving monthly usage information."""
    usage = apify_client.user().monthly_usage()

    assert usage is not None
    # Verify expected fields exist
    assert usage.usage_cycle is not None
    assert isinstance(usage.monthly_service_usage, dict)
    assert isinstance(usage.daily_service_usages, list)
