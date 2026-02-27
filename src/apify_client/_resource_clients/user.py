from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from apify_client._docs import docs_group
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
from apify_client._utils import catch_not_found_or_throw, response_to_dict
from apify_client.errors import ApifyApiError


@docs_group('Resource clients')
class UserClient(ResourceClient):
    """Sub-client for managing user account information.

    Provides methods to manage user account information, e.g. get user data or monthly usage. Obtain an instance via
    an appropriate method on the `ApifyClient` class.
    """

    def __init__(
        self,
        *,
        resource_id: str | None = None,
        resource_path: str = 'users',
        **kwargs: Any,
    ) -> None:
        super().__init__(
            resource_id=resource_id or 'me',
            resource_path=resource_path,
            **kwargs,
        )

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
            json=self._clean_json_payload(
                {
                    'maxMonthlyUsageUsd': max_monthly_usage_usd,
                    'dataRetentionDays': data_retention_days,
                }
            ),
        )


@docs_group('Resource clients')
class UserClientAsync(ResourceClientAsync):
    """Sub-client for managing user account information.

    Provides methods to manage user account information, e.g. get user data or monthly usage. Obtain an instance via
    an appropriate method on the `ApifyClientAsync` class.
    """

    def __init__(
        self,
        *,
        resource_id: str | None = None,
        resource_path: str = 'users',
        **kwargs: Any,
    ) -> None:
        super().__init__(
            resource_id=resource_id or 'me',
            resource_path=resource_path,
            **kwargs,
        )

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
            json=self._clean_json_payload(
                {
                    'maxMonthlyUsageUsd': max_monthly_usage_usd,
                    'dataRetentionDays': data_retention_days,
                }
            ),
        )
