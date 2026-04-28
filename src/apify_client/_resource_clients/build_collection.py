from __future__ import annotations

from typing import TYPE_CHECKING, Any

from apify_client._docs import docs_group
from apify_client._iterable_list_page import (
    _LazyTask,
    build_iterable_list_page,
    build_iterable_list_page_async,
)
from apify_client._models_generated import ListOfBuildsResponse
from apify_client._pagination_classes import (
    ListPageOfBuilds,
    ListPageOfBuildsAsync,
    PaginatedPage,
)
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync

if TYPE_CHECKING:
    from apify_client._models_generated import BuildShort
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
    ) -> ListPageOfBuilds:
        """List all Actor builds.

        List all Actor builds, either of a single Actor, or all user's Actors, depending on where this client
        was initialized from.

        The returned page also supports iteration: `for item in client.list(...)` yields individual builds
        and transparently fetches further pages from the API.

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

        def _callback(**kwargs: Any) -> PaginatedPage[BuildShort]:
            result = self._list(timeout=timeout, **kwargs)
            data = ListOfBuildsResponse.model_validate(result).data
            return PaginatedPage(
                items=data.items,
                count=data.count,
                limit=data.limit,
                total=data.total,
                offset=data.offset,
                desc=data.desc,
            )

        first_page = _callback(limit=limit, offset=offset, desc=desc)
        get_iterator = build_iterable_list_page(_callback, first_page, limit=limit, offset=offset, desc=desc)

        return ListPageOfBuilds(
            _get_iterator=get_iterator,
            items=first_page.items,
            count=first_page.count,
            limit=first_page.limit,
            total=first_page.total,
            offset=first_page.offset,
            desc=first_page.desc,
        )


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
    ) -> ListPageOfBuildsAsync:
        """List all Actor builds.

        List all Actor builds, either of a single Actor, or all user's Actors, depending on where this client
        was initialized from.

        The returned page also supports iteration: `async for item in client.list(...)` yields individual builds
        and transparently fetches further pages from the API.

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

        async def _callback(**kwargs: Any) -> PaginatedPage[BuildShort]:
            result = await self._list(timeout=timeout, **kwargs)
            data = ListOfBuildsResponse.model_validate(result).data
            return PaginatedPage(
                items=data.items,
                count=data.count,
                limit=data.limit,
                total=data.total,
                offset=data.offset,
                desc=data.desc,
            )

        fetch_first_page = _LazyTask(_callback(limit=limit, offset=offset, desc=desc))
        get_async_iterator = build_iterable_list_page_async(
            _callback, fetch_first_page, limit=limit, offset=offset, desc=desc
        )

        return ListPageOfBuildsAsync(
            _awaitable_first_page=fetch_first_page,
            _get_async_iterator=get_async_iterator,
        )
