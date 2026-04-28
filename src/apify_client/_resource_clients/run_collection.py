from __future__ import annotations

from typing import TYPE_CHECKING, Any

from apify_client._docs import docs_group
from apify_client._models_generated import ListOfRunsResponse
from apify_client._pagination import (
    _LazyTask,
    build_get_iterator,
    build_get_iterator_async,
)
from apify_client._pagination_classes import (
    ListPageOfRuns,
    ListPageOfRunsAsync,
    PageOfItems,
)
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync

if TYPE_CHECKING:
    from datetime import datetime

    from apify_client._models_generated import ActorJobStatus, RunShort
    from apify_client._types import Timeout


@docs_group('Resource clients')
class RunCollectionClient(ResourceClient):
    """Sub-client for the Actor run collection.

    Provides methods to manage Actor runs, e.g. list them. Obtain an instance via an appropriate method on the
    `ApifyClient` class.
    """

    def __init__(
        self,
        *,
        resource_path: str = 'actor-runs',
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
        status: ActorJobStatus | list[ActorJobStatus] | None = None,  # ty: ignore[invalid-type-form]
        started_before: str | datetime | None = None,
        started_after: str | datetime | None = None,
        timeout: Timeout = 'medium',
    ) -> ListPageOfRuns:
        """List all Actor runs.

        List all Actor runs, either of a single Actor, or all user's Actors, depending on where this client
        was initialized from.

        The returned page also supports iteration: `for item in client.list(...)` yields individual runs
        and transparently fetches further pages from the API.

        https://docs.apify.com/api/v2#/reference/actors/run-collection/get-list-of-runs
        https://docs.apify.com/api/v2#/reference/actor-runs/run-collection/get-user-runs-list

        Args:
            limit: How many runs to retrieve.
            offset: What run to include as first when retrieving the list.
            desc: Whether to sort the runs in descending order based on their start date.
            status: Retrieve only runs with the provided statuses.
            started_before: Only return runs started before this date (inclusive).
            started_after: Only return runs started after this date (inclusive).
            timeout: Timeout for the API HTTP request.

        Returns:
            The retrieved Actor runs.
        """
        status_param = list(status) if isinstance(status, list) else status

        def _callback(**kwargs: Any) -> PageOfItems[RunShort]:
            result = self._list(
                timeout=timeout,
                status=status_param,
                startedBefore=started_before,
                startedAfter=started_after,
                **kwargs,
            )
            data = ListOfRunsResponse.model_validate(result).data
            return PageOfItems(
                items=data.items,
                count=data.count,
                limit=data.limit,
                total=data.total,
                offset=data.offset,
                desc=data.desc,
            )

        first_page = _callback(limit=limit, offset=offset, desc=desc)
        get_iterator = build_get_iterator(_callback, first_page, limit=limit, offset=offset, desc=desc)

        return ListPageOfRuns(
            _get_iterator=get_iterator,
            items=first_page.items,
            count=first_page.count,
            limit=first_page.limit,
            total=first_page.total,
            offset=first_page.offset,
            desc=first_page.desc,
        )


@docs_group('Resource clients')
class RunCollectionClientAsync(ResourceClientAsync):
    """Sub-client for the Actor run collection.

    Provides methods to manage Actor runs, e.g. list them. Obtain an instance via an appropriate method on the
    `ApifyClientAsync` class.
    """

    def __init__(
        self,
        *,
        resource_path: str = 'actor-runs',
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
        status: ActorJobStatus | list[ActorJobStatus] | None = None,  # ty: ignore[invalid-type-form]
        started_before: str | datetime | None = None,
        started_after: str | datetime | None = None,
        timeout: Timeout = 'medium',
    ) -> ListPageOfRunsAsync:
        """List all Actor runs.

        List all Actor runs, either of a single Actor, or all user's Actors, depending on where this client
        was initialized from.

        The returned page also supports iteration: `async for item in client.list(...)` yields individual runs
        and transparently fetches further pages from the API.

        https://docs.apify.com/api/v2#/reference/actors/run-collection/get-list-of-runs
        https://docs.apify.com/api/v2#/reference/actor-runs/run-collection/get-user-runs-list

        Args:
            limit: How many runs to retrieve.
            offset: What run to include as first when retrieving the list.
            desc: Whether to sort the runs in descending order based on their start date.
            status: Retrieve only runs with the provided statuses.
            started_before: Only return runs started before this date (inclusive).
            started_after: Only return runs started after this date (inclusive).
            timeout: Timeout for the API HTTP request.

        Returns:
            The retrieved Actor runs.
        """
        status_param = list(status) if isinstance(status, list) else status

        async def _callback(**kwargs: Any) -> PageOfItems[RunShort]:
            result = await self._list(
                timeout=timeout,
                status=status_param,
                startedBefore=started_before,
                startedAfter=started_after,
                **kwargs,
            )
            data = ListOfRunsResponse.model_validate(result).data
            return PageOfItems(
                items=data.items,
                count=data.count,
                limit=data.limit,
                total=data.total,
                offset=data.offset,
                desc=data.desc,
            )

        fetch_first_page = _LazyTask(_callback(limit=limit, offset=offset, desc=desc))
        get_async_iterator = build_get_iterator_async(
            _callback, fetch_first_page, limit=limit, offset=offset, desc=desc
        )

        return ListPageOfRunsAsync(
            _awaitable_first_page=fetch_first_page,
            _get_async_iterator=get_async_iterator,
        )
