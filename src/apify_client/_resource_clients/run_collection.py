from __future__ import annotations

from typing import TYPE_CHECKING, Any

from apify_client._docs import docs_group
from apify_client._iterable_list import (
    AwaitableAsyncIterable,
    IterableListOfRuns,
    build_awaitable_async_iterable_offset,
    build_iterable_offset,
    make_iterable_list_of_runs,
)
from apify_client._models import ListOfRuns, ListOfRunsResponse
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync

if TYPE_CHECKING:
    from datetime import datetime

    from apify_client._models import RunShort
    from apify_client._types import ActorJobStatus, Timeout


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
    ) -> IterableListOfRuns:
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

        def _fetch(**kwargs: Any) -> ListOfRuns:
            result = self._list(
                timeout=timeout,
                status=status_param,
                startedBefore=started_before,
                startedAfter=started_after,
                **kwargs,
            )
            return ListOfRunsResponse.model_validate(result).data

        return build_iterable_offset(_fetch, make_iterable_list_of_runs, limit=limit, offset=offset, desc=desc)


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
    ) -> AwaitableAsyncIterable[ListOfRuns, RunShort]:
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

        async def _fetch(**kwargs: Any) -> ListOfRuns:
            result = await self._list(
                timeout=timeout,
                status=status_param,
                startedBefore=started_before,
                startedAfter=started_after,
                **kwargs,
            )
            return ListOfRunsResponse.model_validate(result).data

        return build_awaitable_async_iterable_offset(_fetch, limit=limit, offset=offset, desc=desc)
