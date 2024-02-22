from __future__ import annotations

from typing import Any

from apify_shared.utils import ignore_docs, parse_date_fields

from apify_client._errors import ApifyApiError
from apify_client._utils import catch_not_found_or_throw, pluck_data
from apify_client.clients.base import ResourceClient, ResourceClientAsync


class UserClient(ResourceClient):
    """Sub-client for querying user data."""

    @ignore_docs
    def __init__(self: UserClient, *args: Any, **kwargs: Any) -> None:
        """Initialize the UserClient."""
        resource_id = kwargs.pop('resource_id', None)
        if resource_id is None:
            resource_id = 'me'
        resource_path = kwargs.pop('resource_path', 'users')
        super().__init__(*args, resource_id=resource_id, resource_path=resource_path, **kwargs)

    def get(self: UserClient) -> dict | None:
        """Return information about user account.

        You receive all or only public info based on your token permissions.

        https://docs.apify.com/api/v2#/reference/users

        Returns:
            The retrieved user data, or None if the user does not exist.
        """
        return self._get()

    def monthly_usage(self: UserClient) -> dict | None:
        """Return monthly usage of the user account.

        This includes a complete usage summary for the current usage cycle, an overall sum, as well as a daily breakdown
        of usage. It is the same information which is available on the account's Billing page. The information includes
        use of storage, data transfer, and request queue usage.

        https://docs.apify.com/api/v2/#/reference/users/monthly-usage

        Returns:
            The retrieved request, or None, if it did not exist.
        """
        try:
            response = self.http_client.call(
                url=self._url('usage/monthly'),
                method='GET',
                params=self._params(),
            )
            return parse_date_fields(pluck_data(response.json()))

        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

        return None

    def limits(self: UserClient) -> dict | None:
        """Returns a complete summary of the user account's limits.

        It is the same information which is available on the account's Limits page. The returned data includes the current
        usage cycle, a summary of the account's limits, and the current usage.

        https://docs.apify.com/api/v2#/reference/request-queues/request/get-request

        Returns:
            The retrieved request, or None, if it did not exist.
        """
        try:
            response = self.http_client.call(
                url=self._url('limits'),
                method='GET',
                params=self._params(),
            )
            return parse_date_fields(pluck_data(response.json()))

        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

        return None


class UserClientAsync(ResourceClientAsync):
    """Async sub-client for querying user data."""

    @ignore_docs
    def __init__(self: UserClientAsync, *args: Any, **kwargs: Any) -> None:
        """Initialize the UserClientAsync."""
        resource_id = kwargs.pop('resource_id', None)
        if resource_id is None:
            resource_id = 'me'
        resource_path = kwargs.pop('resource_path', 'users')
        super().__init__(*args, resource_id=resource_id, resource_path=resource_path, **kwargs)

    async def get(self: UserClientAsync) -> dict | None:
        """Return information about user account.

        You receive all or only public info based on your token permissions.

        https://docs.apify.com/api/v2#/reference/users

        Returns:
            The retrieved user data, or None if the user does not exist.
        """
        return await self._get()

    async def monthly_usage(self: UserClientAsync) -> dict | None:
        """Return monthly usage of the user account.

        This includes a complete usage summary for the current usage cycle, an overall sum, as well as a daily breakdown
        of usage. It is the same information which is available on the account's Billing page. The information includes
        use of storage, data transfer, and request queue usage.

        https://docs.apify.com/api/v2/#/reference/users/monthly-usage

        Returns:
            The retrieved request, or None, if it did not exist.
        """
        try:
            response = await self.http_client.call(
                url=self._url('usage/monthly'),
                method='GET',
                params=self._params(),
            )
            return parse_date_fields(pluck_data(response.json()))

        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

        return None

    async def limits(self: UserClientAsync) -> dict | None:
        """Returns a complete summary of the user account's limits.

        It is the same information which is available on the account's Limits page. The returned data includes the current
        usage cycle, a summary of the account's limits, and the current usage.

        https://docs.apify.com/api/v2#/reference/request-queues/request/get-request

        Returns:
            The retrieved request, or None, if it did not exist.
        """
        try:
            response = await self.http_client.call(
                url=self._url('limits'),
                method='GET',
                params=self._params(),
            )
            return parse_date_fields(pluck_data(response.json()))

        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

        return None
