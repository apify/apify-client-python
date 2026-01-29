from __future__ import annotations

from typing import TYPE_CHECKING, Any

from apify_client._models import GetListOfRunsResponse, ListOfRuns, RunShort
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync
from apify_client._utils import enum_to_value, response_to_dict

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator
    from datetime import datetime

    from apify_client._consts import ActorJobStatus


class RunCollectionClient(ResourceClient):
    """Sub-client for listing Actor runs."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'actor-runs')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
        status: ActorJobStatus | list[ActorJobStatus] | None = None,  # ty: ignore[invalid-type-form]
        started_before: str | datetime | None = None,
        started_after: str | datetime | None = None,
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

        Returns:
            The retrieved Actor runs.
        """
        status_param = [enum_to_value(s) for s in status] if isinstance(status, list) else enum_to_value(status)

        response = self._http_client.call(
            url=self._build_url(),
            method='GET',
            params=self._build_params(
                limit=limit,
                offset=offset,
                desc=desc,
                status=status_param,
                startedBefore=started_before,
                startedAfter=started_after,
            ),
        )
        response_as_dict = response_to_dict(response)
        return GetListOfRunsResponse.model_validate(response_as_dict).data

    def iterate(
        self,
        *,
        limit: int | None = None,
        desc: bool | None = None,
        status: ActorJobStatus | list[ActorJobStatus] | None = None,  # ty: ignore[invalid-type-form]
        started_before: str | datetime | None = None,
        started_after: str | datetime | None = None,
    ) -> Iterator[RunShort]:
        """Iterate over all Actor runs.

        Iterate over all Actor runs, either of a single Actor, or all user's Actors, depending on where this client
        was initialized from.

        https://docs.apify.com/api/v2#/reference/actors/run-collection/get-list-of-runs
        https://docs.apify.com/api/v2#/reference/actor-runs/run-collection/get-user-runs-list

        Args:
            limit: Maximum number of runs to return. By default there is no limit.
            desc: Whether to sort the runs in descending order based on their start date.
            status: Retrieve only runs with the provided statuses.
            started_before: Only return runs started before this date (inclusive).
            started_after: Only return runs started after this date (inclusive).

        Yields:
            A run from the collection.
        """
        cache_size = 1000
        read_items = 0
        offset = 0

        while True:
            effective_limit = cache_size
            if limit is not None:
                if read_items == limit:
                    break
                effective_limit = min(cache_size, limit - read_items)

            current_page = self.list(
                limit=effective_limit,
                offset=offset,
                desc=desc,
                status=status,
                started_before=started_before,
                started_after=started_after,
            )

            yield from current_page.items

            current_page_item_count = len(current_page.items)
            read_items += current_page_item_count
            offset += current_page_item_count

            if current_page_item_count < cache_size:
                break


class RunCollectionClientAsync(ResourceClientAsync):
    """Async sub-client for listing Actor runs."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'actor-runs')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
        status: ActorJobStatus | list[ActorJobStatus] | None = None,  # ty: ignore[invalid-type-form]
        started_before: str | datetime | None = None,
        started_after: str | datetime | None = None,
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

        Returns:
            The retrieved Actor runs.
        """
        status_param = [enum_to_value(s) for s in status] if isinstance(status, list) else enum_to_value(status)

        response = await self._http_client.call(
            url=self._build_url(),
            method='GET',
            params=self._build_params(
                limit=limit,
                offset=offset,
                desc=desc,
                status=status_param,
                startedBefore=started_before,
                startedAfter=started_after,
            ),
        )
        response_as_dict = response_to_dict(response)
        return GetListOfRunsResponse.model_validate(response_as_dict).data

    async def iterate(
        self,
        *,
        limit: int | None = None,
        desc: bool | None = None,
        status: ActorJobStatus | list[ActorJobStatus] | None = None,  # ty: ignore[invalid-type-form]
        started_before: str | datetime | None = None,
        started_after: str | datetime | None = None,
    ) -> AsyncIterator[RunShort]:
        """Iterate over all Actor runs.

        Iterate over all Actor runs, either of a single Actor, or all user's Actors, depending on where this client
        was initialized from.

        https://docs.apify.com/api/v2#/reference/actors/run-collection/get-list-of-runs
        https://docs.apify.com/api/v2#/reference/actor-runs/run-collection/get-user-runs-list

        Args:
            limit: Maximum number of runs to return. By default there is no limit.
            desc: Whether to sort the runs in descending order based on their start date.
            status: Retrieve only runs with the provided statuses.
            started_before: Only return runs started before this date (inclusive).
            started_after: Only return runs started after this date (inclusive).

        Yields:
            A run from the collection.
        """
        cache_size = 1000
        read_items = 0
        offset = 0

        while True:
            effective_limit = cache_size
            if limit is not None:
                if read_items == limit:
                    break
                effective_limit = min(cache_size, limit - read_items)

            current_page = await self.list(
                limit=effective_limit,
                offset=offset,
                desc=desc,
                status=status,
                started_before=started_before,
                started_after=started_after,
            )

            for item in current_page.items:
                yield item

            current_page_item_count = len(current_page.items)
            read_items += current_page_item_count
            offset += current_page_item_count

            if current_page_item_count < cache_size:
                break
