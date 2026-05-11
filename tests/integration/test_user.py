"""Unified tests for user (sync + async)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ._utils import maybe_await
from apify_client._models import AccountLimits, MonthlyUsage, UserPrivateInfo, UserPublicInfo
from apify_client.errors import ApifyApiError

if TYPE_CHECKING:
    from apify_client import ApifyClient, ApifyClientAsync


async def test_get_user(client: ApifyClient | ApifyClientAsync) -> None:
    """Test getting user information."""
    user = await maybe_await(client.user().get())
    assert isinstance(user, UserPublicInfo | UserPrivateInfo)
    # UserPublicInfo has username but not id
    assert user.username is not None


async def test_limits(client: ApifyClient | ApifyClientAsync) -> None:
    """Test getting account limits."""
    limits = await maybe_await(client.user().limits())
    # Verify we have at least some limit information. The actual fields depend on the account type.
    assert isinstance(limits, AccountLimits)


async def test_monthly_usage(client: ApifyClient | ApifyClientAsync) -> None:
    """Test retrieving monthly usage information."""
    usage = await maybe_await(client.user().monthly_usage())
    assert isinstance(usage, MonthlyUsage)
    # Verify expected fields exist
    assert usage.usage_cycle is not None
    assert isinstance(usage.monthly_service_usage, dict)
    assert isinstance(usage.daily_service_usages, list)


async def test_update_limits(client: ApifyClient | ApifyClientAsync) -> None:
    """Test updating account limits.

    Note: This test verifies that the update_limits method can be called. On free accounts, the API will reject
    changes to maxMonthlyUsageUsd, but dataRetentionDays can potentially be updated.
    """
    user_client = client.user()

    # Get current limits to see what's available
    current_limits = await maybe_await(user_client.limits())
    assert isinstance(current_limits, AccountLimits)

    # Try to update data retention days (allowed on most accounts). We try to set it to the current
    # value or a reasonable default.
    try:
        # Try updating with just data_retention_days
        await maybe_await(user_client.update_limits(data_retention_days=7))
        # If it succeeds, the update was applied (or same value was set)
    except ApifyApiError as exc:
        # Some accounts may not allow updating limits - re-raise if unexpected.
        # This is expected for certain account types.
        if exc.status_code not in [400, 403]:
            raise
