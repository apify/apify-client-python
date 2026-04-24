from __future__ import annotations

from typing import TYPE_CHECKING, Any

from apify_client._docs import docs_group
from apify_client._iterable_list import (
    AwaitableAsyncIterable,
    IterableListOfBuilds,
    build_awaitable_async_iterable_offset,
    build_iterable_offset,
    make_iterable_list_of_builds,
)
from apify_client._models import ListOfBuilds, ListOfBuildsResponse
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync

if TYPE_CHECKING:
    from apify_client._models import BuildShort
    from apify_client._types import Timeout


@docs_group('Resource clients')
class BuildCollectionClient(ResourceClient):
    """Sub-client for the Actor build collection.

    Provides methods to manage Actor builds, e.g. list them. Obtain an instance via an appropriate method on the
    `ApifyClient` class.
    """

    def __init__(
        self,
        *,
        resource_path: str = 'actor-builds',
        **kwargs: Any,
    ) -> None:
        super().__init__(
            resource_path=resource_path,
            **kwargs,
        )

    def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
        timeout: Timeout = 'medium',
    ) -> IterableListOfBuilds:
        """List all Actor builds.

        List all Actor builds, either of a single Actor, or all user's Actors, depending on where this client
        was initialized from.

        The returned value has the fields of `ListOfBuilds` and additionally implements `Iterable[BuildShort]`:
        iterate with `for item in client.list(...)` to transparently fetch further pages.

        https://docs.apify.com/api/v2#/reference/actors/build-collection/get-list-of-builds
        https://docs.apify.com/api/v2#/reference/actor-builds/build-collection/get-user-builds-list

        Args:
            limit: How many builds to retrieve.
            offset: What build to include as first when retrieving the list.
            desc: Whether to sort the builds in descending order based on their start date.
            timeout: Timeout for the API HTTP request.

        Returns:
            The retrieved Actor builds.
        """

        def _fetch(**kwargs: Any) -> ListOfBuilds:
            result = self._list(timeout=timeout, **kwargs)
            return ListOfBuildsResponse.model_validate(result).data

        return build_iterable_offset(_fetch, make_iterable_list_of_builds, limit=limit, offset=offset, desc=desc)


@docs_group('Resource clients')
class BuildCollectionClientAsync(ResourceClientAsync):
    """Sub-client for the Actor build collection.

    Provides methods to manage Actor builds, e.g. list them. Obtain an instance via an appropriate method on the
    `ApifyClientAsync` class.
    """

    def __init__(
        self,
        *,
        resource_path: str = 'actor-builds',
        **kwargs: Any,
    ) -> None:
        super().__init__(
            resource_path=resource_path,
            **kwargs,
        )

    def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
        timeout: Timeout = 'medium',
    ) -> AwaitableAsyncIterable[ListOfBuilds, BuildShort]:
        """List all Actor builds.

        List all Actor builds, either of a single Actor, or all user's Actors, depending on where this client
        was initialized from.

        The returned value has the fields of `ListOfBuilds` and additionally implements `Iterable[BuildShort]`:
        iterate with `for item in client.list(...)` to transparently fetch further pages.

        https://docs.apify.com/api/v2#/reference/actors/build-collection/get-list-of-builds
        https://docs.apify.com/api/v2#/reference/actor-builds/build-collection/get-user-builds-list

        Args:
            limit: How many builds to retrieve.
            offset: What build to include as first when retrieving the list.
            desc: Whether to sort the builds in descending order based on their start date.
            timeout: Timeout for the API HTTP request.

        Returns:
            The retrieved Actor builds.
        """

        async def _fetch(**kwargs: Any) -> ListOfBuilds:
            result = await self._list(timeout=timeout, **kwargs)
            return ListOfBuildsResponse.model_validate(result).data

        return build_awaitable_async_iterable_offset(_fetch, limit=limit, offset=offset, desc=desc)
