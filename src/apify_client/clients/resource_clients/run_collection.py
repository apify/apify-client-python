from typing import Any, Optional

from ..._utils import ListPage, _make_async_docs, _maybe_extract_enum_member_value
from ...consts import ActorJobStatus
from ..base import ResourceCollectionClient, ResourceCollectionClientAsync


class RunCollectionClient(ResourceCollectionClient):
    """Sub-client for listing actor runs."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the RunCollectionClient."""
        resource_path = kwargs.pop('resource_path', 'actor-runs')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def list(
        self,
        *,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        desc: Optional[bool] = None,
        status: Optional[ActorJobStatus] = None,
    ) -> ListPage:
        """List all actor runs (either of a single actor, or all user's actors, depending on where this client was initialized from).

        https://docs.apify.com/api/v2#/reference/actors/run-collection/get-list-of-runs
        https://docs.apify.com/api/v2#/reference/actor-runs/run-collection/get-user-runs-list

        Args:
            limit (int, optional): How many runs to retrieve
            offset (int, optional): What run to include as first when retrieving the list
            desc (bool, optional): Whether to sort the runs in descending order based on their start date
            status (ActorJobStatus, optional): Retrieve only runs with the provided status

        Returns:
            ListPage: The retrieved actor runs
        """
        return self._list(
            limit=limit,
            offset=offset,
            desc=desc,
            status=_maybe_extract_enum_member_value(status),
        )


class RunCollectionClientAsync(ResourceCollectionClientAsync):
    """Async sub-client for listing actor runs."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the RunCollectionClientAsync."""
        resource_path = kwargs.pop('resource_path', 'actor-runs')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    @_make_async_docs(src=RunCollectionClient.list)
    async def list(
        self,
        *,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        desc: Optional[bool] = None,
        status: Optional[ActorJobStatus] = None,
    ) -> ListPage:
        return await self._list(
            limit=limit,
            offset=offset,
            desc=desc,
            status=_maybe_extract_enum_member_value(status),
        )
