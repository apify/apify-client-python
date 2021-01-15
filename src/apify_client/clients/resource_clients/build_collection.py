from typing import Any, Dict, Optional

from ..base.resource_collection_client import ResourceCollectionClient


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

        Returns:
            The retrieved builds of a user
        """
        return self._list(limit=limit, offset=offset, desc=desc)
