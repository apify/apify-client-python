from typing import Any, Dict, Optional

from ..base.resource_client import ResourceClient


class UserClient(ResourceClient):
    """Sub-client for querying user data."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the UserClient."""
        super().__init__(*args, resource_path='users', **kwargs)

    def get(self) -> Optional[Dict]:
        """Return information about user account.

        You receive all or only public info based on your token permissions.

        https://docs.apify.com/api/v2#/reference/users

        Returns:
            The retrieved user data
        """
        return self._get()
