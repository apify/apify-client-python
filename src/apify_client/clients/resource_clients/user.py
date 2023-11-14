from __future__ import annotations

from apify_shared.utils import ignore_docs

from ..base import ResourceClient, ResourceClientAsync


class UserClient(ResourceClient):
    """Sub-client for querying user data."""

    @ignore_docs
    def __init__(self: UserClient, *args: tuple, **kwargs: dict) -> None:
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
            dict, optional: The retrieved user data, or None if the user does not exist.
        """
        return self._get()


class UserClientAsync(ResourceClientAsync):
    """Async sub-client for querying user data."""

    @ignore_docs
    def __init__(self: UserClientAsync, *args: tuple, **kwargs: dict) -> None:
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
            dict, optional: The retrieved user data, or None if the user does not exist.
        """
        return await self._get()
