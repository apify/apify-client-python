from __future__ import annotations

from typing import TYPE_CHECKING, Any

from apify_client._docs import docs_group
from apify_client._models import ListOfRuns, ListOfRunsResponse
from apify_client._pagination import get_items_iterator, get_items_iterator_async
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator
    from datetime import datetime

    from apify_client._literals import ActorJobStatus
    from apify_client._models import RunShort
    from apify_client.types import Timeout


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
    ) -> ListOfRuns:
        """List all Actor runs.

        List all Actor runs, either of a single Actor, or all user's Actors, depending on where this client
        was initialized from.

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

        result = self._list(
            timeout=timeout,
            limit=limit,
            offset=offset,
            desc=desc,
            status=status_param,
            startedBefore=started_before,
            startedAfter=started_after,
        )
        return ListOfRunsResponse.model_validate(result).data

    def iterate(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
        status: ActorJobStatus | list[ActorJobStatus] | None = None,  # ty: ignore[invalid-type-form]
        started_before: str | datetime | None = None,
        started_after: str | datetime | None = None,
        timeout: Timeout = 'medium',
    ) -> Iterator[RunShort]:
        """Iterate over all Actor runs.

        Simple `list` does only one API call, possibly not listing all items matching the criteria. This method
        returns an iterator that is capable of making multiple API calls to retrieve all items matching the criteria.

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

        Yields:
            The Actor runs matching the specified filters.
        """

        def _callback(*, limit: int | None = None, offset: int | None = None) -> ListOfRuns:
            return self.list(
                limit=limit,
                offset=offset,
                desc=desc,
                status=status,
                started_before=started_before,
                started_after=started_after,
                timeout=timeout,
            )

        return get_items_iterator(_callback, limit=limit, offset=offset)


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

    async def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
        status: ActorJobStatus | list[ActorJobStatus] | None = None,  # ty: ignore[invalid-type-form]
        started_before: str | datetime | None = None,
        started_after: str | datetime | None = None,
        timeout: Timeout = 'medium',
    ) -> ListOfRuns:
        """List all Actor runs.

        List all Actor runs, either of a single Actor, or all user's Actors, depending on where this client
        was initialized from.

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

        result = await self._list(
            timeout=timeout,
            limit=limit,
            offset=offset,
            desc=desc,
            status=status_param,
            startedBefore=started_before,
            startedAfter=started_after,
        )
        return ListOfRunsResponse.model_validate(result).data

    def iterate(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
        status: ActorJobStatus | list[ActorJobStatus] | None = None,  # ty: ignore[invalid-type-form]
        started_before: str | datetime | None = None,
        started_after: str | datetime | None = None,
        timeout: Timeout = 'medium',
    ) -> AsyncIterator[RunShort]:
        """Iterate over all Actor runs.

        Simple `list` does only one API call, possibly not listing all items matching the criteria. This method
        returns an iterator that is capable of making multiple API calls to retrieve all items matching the criteria.

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

        Yields:
            The Actor runs matching the specified filters.
        """

        async def _callback(*, limit: int | None = None, offset: int | None = None) -> ListOfRuns:
            return await self.list(
                limit=limit,
                offset=offset,
                desc=desc,
                status=status,
                started_before=started_before,
                started_after=started_after,
                timeout=timeout,
            )

        return get_items_iterator_async(_callback, limit=limit, offset=offset)
