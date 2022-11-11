from typing import Any, Dict, Optional

from ..._utils import _make_async_docs
from ..base import ResourceClient, ResourceClientAsync


class UserClient(ResourceClient):
    """Sub-client for querying user data."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the UserClient."""
        resource_id = kwargs.pop('resource_id', 'me')
        resource_path = kwargs.pop('resource_path', 'users')
        super().__init__(*args, resource_id=resource_id, resource_path=resource_path, **kwargs)

    def get(self) -> Optional[Dict]:
        """Return information about user account.

        You receive all or only public info based on your token permissions.

        https://docs.apify.com/api/v2#/reference/users

        Returns:
            dict, optional: The retrieved user data, or None if the user does not exist.
        """
        return self._get()


class UserClientAsync(ResourceClientAsync):
    """Async sub-client for querying user data."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the UserClientAsync."""
        resource_id = kwargs.pop('resource_id', 'me')
        resource_path = kwargs.pop('resource_path', 'users')
        super().__init__(*args, resource_id=resource_id, resource_path=resource_path, **kwargs)

    @_make_async_docs(src=UserClient.get)
    async def get(self) -> Optional[Dict]:
        return await self._get()
