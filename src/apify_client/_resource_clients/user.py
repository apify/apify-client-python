from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from apify_client._models import (
    AccountLimits,
    LimitsResponse,
    MonthlyUsage,
    MonthlyUsageResponse,
    PrivateUserDataResponse,
    PublicUserDataResponse,
    UserPrivateInfo,
    UserPublicInfo,
)
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync
from apify_client._utils import catch_not_found_or_throw, filter_none_values, response_to_dict
from apify_client.errors import ApifyApiError


class UserClient(ResourceClient):
    """Sub-client for querying user data."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_id = kwargs.pop('resource_id', None)
        if resource_id is None:
            resource_id = 'me'
        resource_path = kwargs.pop('resource_path', 'users')
        super().__init__(*args, resource_id=resource_id, resource_path=resource_path, **kwargs)

    def get(self) -> UserPublicInfo | UserPrivateInfo | None:
        """Return information about user account.

        You receive all or only public info based on your token permissions.

        https://docs.apify.com/api/v2#/reference/users

        Returns:
            The retrieved user data, or None if the user does not exist.
        """
        result = self._get()
        if result is None:
            return None
        try:
            return PrivateUserDataResponse.model_validate(result).data
        except ValidationError:
            return PublicUserDataResponse.model_validate(result).data

    def monthly_usage(self) -> MonthlyUsage | None:
        """Return monthly usage of the user account.

        This includes a complete usage summary for the current usage cycle, an overall sum, as well as a daily breakdown
        of usage. It is the same information which is available on the account's Billing page. The information includes
        use of storage, data transfer, and request queue usage.

        https://docs.apify.com/api/v2/#/reference/users/monthly-usage

        Returns:
            The retrieved request, or None, if it did not exist.
        """
        try:
            response = self._http_client.call(
                url=self._build_url('usage/monthly'),
                method='GET',
                params=self._build_params(),
            )
            result = response_to_dict(response)
            return MonthlyUsageResponse.model_validate(result).data

        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

        return None

    def limits(self) -> AccountLimits | None:
        """Return a complete summary of the user account's limits.

        It is the same information which is available on the account's Limits page. The returned data includes
        the current usage cycle, a summary of the account's limits, and the current usage.

        https://docs.apify.com/api/v2#/reference/users/account-limits/get-account-limits

        Returns:
            The account limits, or None, if they could not be retrieved.
        """
        try:
            response = self._http_client.call(
                url=self._build_url('limits'),
                method='GET',
                params=self._build_params(),
            )
            result = response_to_dict(response)
            return LimitsResponse.model_validate(result).data

        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

        return None

    def update_limits(
        self,
        *,
        max_monthly_usage_usd: int | None = None,
        data_retention_days: int | None = None,
    ) -> None:
        """Update the account's limits manageable on your account's Limits page."""
        self._http_client.call(
            url=self._build_url('limits'),
            method='PUT',
            params=self._build_params(),
            json=filter_none_values(
                {
                    'maxMonthlyUsageUsd': max_monthly_usage_usd,
                    'dataRetentionDays': data_retention_days,
                }
            ),
        )


class UserClientAsync(ResourceClientAsync):
    """Async sub-client for querying user data."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_id = kwargs.pop('resource_id', None)
        if resource_id is None:
            resource_id = 'me'
        resource_path = kwargs.pop('resource_path', 'users')
        super().__init__(*args, resource_id=resource_id, resource_path=resource_path, **kwargs)

    async def get(self) -> UserPublicInfo | UserPrivateInfo | None:
        """Return information about user account.

        You receive all or only public info based on your token permissions.

        https://docs.apify.com/api/v2#/reference/users

        Returns:
            The retrieved user data, or None if the user does not exist.
        """
        result = await self._get()
        if result is None:
            return None
        try:
            return PrivateUserDataResponse.model_validate(result).data
        except ValidationError:
            return PublicUserDataResponse.model_validate(result).data

    async def monthly_usage(self) -> MonthlyUsage | None:
        """Return monthly usage of the user account.

        This includes a complete usage summary for the current usage cycle, an overall sum, as well as a daily breakdown
        of usage. It is the same information which is available on the account's Billing page. The information includes
        use of storage, data transfer, and request queue usage.

        https://docs.apify.com/api/v2/#/reference/users/monthly-usage

        Returns:
            The retrieved request, or None, if it did not exist.
        """
        try:
            response = await self._http_client.call(
                url=self._build_url('usage/monthly'),
                method='GET',
                params=self._build_params(),
            )
            result = response_to_dict(response)
            return MonthlyUsageResponse.model_validate(result).data

        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

        return None

    async def limits(self) -> AccountLimits | None:
        """Return a complete summary of the user account's limits.

        It is the same information which is available on the account's Limits page. The returned data includes
        the current usage cycle, a summary of the account's limits, and the current usage.

        https://docs.apify.com/api/v2#/reference/users/account-limits/get-account-limits

        Returns:
            The account limits, or None, if they could not be retrieved.
        """
        try:
            response = await self._http_client.call(
                url=self._build_url('limits'),
                method='GET',
                params=self._build_params(),
            )
            result = response_to_dict(response)
            return LimitsResponse.model_validate(result).data

        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

        return None

    async def update_limits(
        self,
        *,
        max_monthly_usage_usd: int | None = None,
        data_retention_days: int | None = None,
    ) -> None:
        """Update the account's limits manageable on your account's Limits page."""
        await self._http_client.call(
            url=self._build_url('limits'),
            method='PUT',
            params=self._build_params(),
            json=filter_none_values(
                {
                    'maxMonthlyUsageUsd': max_monthly_usage_usd,
                    'dataRetentionDays': data_retention_days,
                }
            ),
        )
