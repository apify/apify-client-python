from typing import Any, Optional

from ..._utils import ListPage
from ..base import ResourceCollectionClient


class BuildCollectionClient(ResourceCollectionClient):
    """Sub-client for listing actor builds."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the BuildCollectionClient."""
        resource_path = kwargs.pop('resource_path', 'actor-builds')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def list(
        self,
        *,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        desc: Optional[bool] = None,
    ) -> ListPage:
        """List all actor builds (either of a single actor, or all user's actors, depending on where this client was initialized from).

        https://docs.apify.com/api/v2#/reference/actors/build-collection/get-list-of-builds
        https://docs.apify.com/api/v2#/reference/actor-builds/build-collection/get-user-builds-list

        Args:
            limit (int, optional): How many builds to retrieve
            offset (int, optional): What build to include as first when retrieving the list
            desc (bool, optional): Whether to sort the builds in descending order based on their start date

        Returns:
            ListPage: The retrieved actor builds
        """
        return self._list(limit=limit, offset=offset, desc=desc)
