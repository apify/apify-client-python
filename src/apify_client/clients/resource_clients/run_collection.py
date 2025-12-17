from __future__ import annotations

from typing import TYPE_CHECKING, Any

from apify_client._utils import maybe_extract_enum_member_value
from apify_client.clients.base import ResourceCollectionClient, ResourceCollectionClientAsync

if TYPE_CHECKING:
    from datetime import datetime

    from apify_shared.consts import ActorJobStatus

    from apify_client.clients.base.resource_collection_client import ListPage


class RunCollectionClient(ResourceCollectionClient):
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
    ) -> ListPage[dict]:
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
        if isinstance(status, list):
            status_param = [maybe_extract_enum_member_value(s) for s in status]
        else:
            status_param = maybe_extract_enum_member_value(status)

        return self._list(
            limit=limit,
            offset=offset,
            desc=desc,
            status=status_param,
            startedBefore=started_before,
            startedAfter=started_after,
        )


class RunCollectionClientAsync(ResourceCollectionClientAsync):
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
    ) -> ListPage[dict]:
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
        if isinstance(status, list):
            status_param = [maybe_extract_enum_member_value(s) for s in status]
        else:
            status_param = maybe_extract_enum_member_value(status)

        return await self._list(
            limit=limit,
            offset=offset,
            desc=desc,
            status=status_param,
            startedBefore=started_before,
            startedAfter=started_after,
        )
