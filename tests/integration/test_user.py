from __future__ import annotations

from typing import TYPE_CHECKING

from apify_client.errors import ApifyApiError

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

    # Verify we have at least some limit information. The actual fields depend on the account type.
    assert limits is not None


def test_monthly_usage(apify_client: ApifyClient) -> None:
    """Test retrieving monthly usage information."""
    usage = apify_client.user().monthly_usage()

    assert usage is not None
    # Verify expected fields exist
    assert usage.usage_cycle is not None
    assert isinstance(usage.monthly_service_usage, dict)
    assert isinstance(usage.daily_service_usages, list)


def test_update_limits(apify_client: ApifyClient) -> None:
    """Test updating account limits.

    Note: This test verifies that the update_limits method can be called. On free accounts, the API will reject
    changes to maxMonthlyUsageUsd, but dataRetentionDays can potentially be updated.
    """
    user_client = apify_client.user()

    # Get current limits to see what's available
    current_limits = user_client.limits()
    assert current_limits is not None

    # Try to update data retention days (allowed on most accounts). We try to set it to the current
    # value or a reasonable default.
    try:
        # Try updating with just data_retention_days
        user_client.update_limits(data_retention_days=7)
        # If it succeeds, the update was applied (or same value was set)
    except ApifyApiError as exc:
        # Some accounts may not allow updating limits - re-raise if unexpected.
        # This is expected for certain account types.
        if exc.status_code not in [400, 403]:
            raise
