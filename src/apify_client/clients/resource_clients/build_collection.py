from typing import Any, Dict, Optional

from ..base import ResourceCollectionClient


class BuildCollectionClient(ResourceCollectionClient):
    """Sub-client for listing user builds.

    Note that this client is not specific for a particular actor but queries all builds for a user based on the provided API token.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the BuildCollectionClient."""
        super().__init__(*args, resource_path='actor-builds', **kwargs)

    def list(self, *, limit: Optional[int] = None, offset: Optional[int] = None, desc: Optional[bool] = None) -> Dict:
        """List all builds of a user.

        https://docs.apify.com/api/v2#/reference/actor-builds/build-collection/get-user-builds-list

        Args:
            limit (int, optional): How many builds to retrieve
            offset (int, optional): What build store to include as first when retrieving the list
            desc (bool, optional): Whether to sort the builds in descending order based on their modification date

        Returns:
            dict: The retrieved builds of a user
        """
        return self._list(limit=limit, offset=offset, desc=desc)
