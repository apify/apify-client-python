from __future__ import annotations

from typing import TYPE_CHECKING, Any

from apify_shared.utils import ignore_docs

from apify_client.clients.base import ResourceCollectionClient, ResourceCollectionClientAsync

if TYPE_CHECKING:
    from apify_shared.models import ListPage


class BuildCollectionClient(ResourceCollectionClient):
    """Sub-client for listing Actor builds."""

    @ignore_docs
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'actor-builds')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
    ) -> ListPage[dict]:
        """List all Actor builds.

        List all Actor builds, either of a single Actor, or all user's Actors, depending on where this client
        was initialized from.

        https://docs.apify.com/api/v2#/reference/actors/build-collection/get-list-of-builds
        https://docs.apify.com/api/v2#/reference/actor-builds/build-collection/get-user-builds-list

        Args:
            limit: How many builds to retrieve.
            offset: What build to include as first when retrieving the list.
            desc: Whether to sort the builds in descending order based on their start date.

        Returns:
            The retrieved Actor builds.
        """
        return self._list(limit=limit, offset=offset, desc=desc)


class BuildCollectionClientAsync(ResourceCollectionClientAsync):
    """Async sub-client for listing Actor builds."""

    @ignore_docs
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'actor-builds')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
    ) -> ListPage[dict]:
        """List all Actor builds.

        List all Actor builds, either of a single Actor, or all user's Actors, depending on where this client
        was initialized from.

        https://docs.apify.com/api/v2#/reference/actors/build-collection/get-list-of-builds
        https://docs.apify.com/api/v2#/reference/actor-builds/build-collection/get-user-builds-list

        Args:
            limit: How many builds to retrieve.
            offset: What build to include as first when retrieving the list.
            desc: Whether to sort the builds in descending order based on their start date.

        Returns:
            The retrieved Actor builds.
        """
        return await self._list(limit=limit, offset=offset, desc=desc)
