from __future__ import annotations

from typing import TYPE_CHECKING, Any

from apify_shared.utils import ignore_docs, maybe_extract_enum_member_value

from apify_client.clients.base import ResourceCollectionClient, ResourceCollectionClientAsync

if TYPE_CHECKING:
    from apify_shared.consts import ActorJobStatus
    from apify_shared.models import ListPage


class RunCollectionClient(ResourceCollectionClient):
    """Sub-client for listing Actor runs."""

    @ignore_docs
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'actor-runs')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
        status: ActorJobStatus | None = None,
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
            status: Retrieve only runs with the provided status.

        Returns:
            The retrieved Actor runs.
        """
        return self._list(
            limit=limit,
            offset=offset,
            desc=desc,
            status=maybe_extract_enum_member_value(status),
        )


class RunCollectionClientAsync(ResourceCollectionClientAsync):
    """Async sub-client for listing Actor runs."""

    @ignore_docs
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'actor-runs')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
        status: ActorJobStatus | None = None,
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
            status: Retrieve only runs with the provided status.

        Returns:
            The retrieved Actor runs.
        """
        return await self._list(
            limit=limit,
            offset=offset,
            desc=desc,
            status=maybe_extract_enum_member_value(status),
        )
