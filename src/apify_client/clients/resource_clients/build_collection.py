from __future__ import annotations

from typing import TYPE_CHECKING, Any

from apify_shared.utils import ignore_docs

from ..base import ResourceCollectionClient, ResourceCollectionClientAsync

if TYPE_CHECKING:
    from apify_shared.models import ListPage


class BuildCollectionClient(ResourceCollectionClient):
    """Sub-client for listing actor builds."""

    @ignore_docs
    def __init__(self: BuildCollectionClient, *args: Any, **kwargs: Any) -> None:
        """Initialize the BuildCollectionClient."""
        resource_path = kwargs.pop('resource_path', 'actor-builds')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def list(  # noqa: A003
        self: BuildCollectionClient,
        *,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
    ) -> ListPage[dict]:
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


class BuildCollectionClientAsync(ResourceCollectionClientAsync):
    """Async sub-client for listing actor builds."""

    @ignore_docs
    def __init__(self: BuildCollectionClientAsync, *args: Any, **kwargs: Any) -> None:
        """Initialize the BuildCollectionClientAsync."""
        resource_path = kwargs.pop('resource_path', 'actor-builds')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def list(  # noqa: A003
        self: BuildCollectionClientAsync,
        *,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
    ) -> ListPage[dict]:
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
        return await self._list(limit=limit, offset=offset, desc=desc)
