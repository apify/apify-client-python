from typing import Any, Dict, Optional

from ..._utils import ListPage, _make_async_docs
from ..base import ResourceCollectionClient, ResourceCollectionClientAsync


class RequestQueueCollectionClient(ResourceCollectionClient):
    """Sub-client for manipulating request queues."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the RequestQueueCollectionClient with the passed arguments."""
        resource_path = kwargs.pop('resource_path', 'request-queues')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def list(
        self,
        *,
        unnamed: Optional[bool] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        desc: Optional[bool] = None,
    ) -> ListPage:
        """List the available request queues.

        https://docs.apify.com/api/v2#/reference/request-queues/queue-collection/get-list-of-request-queues

        Args:
            unnamed (bool, optional): Whether to include unnamed request queues in the list
            limit (int, optional): How many request queues to retrieve
            offset (int, optional): What request queue to include as first when retrieving the list
            desc (bool, optional): Whether to sort therequest queues in descending order based on their modification date

        Returns:
            ListPage: The list of available request queues matching the specified filters.
        """
        return self._list(unnamed=unnamed, limit=limit, offset=offset, desc=desc)

    def get_or_create(self, *, name: Optional[str] = None) -> Dict:
        """Retrieve a named request queue, or create a new one when it doesn't exist.

        https://docs.apify.com/api/v2#/reference/request-queues/queue-collection/create-request-queue

        Args:
            name (str, optional): The name of the request queue to retrieve or create.

        Returns:
            dict: The retrieved or newly-created request queue.
        """
        return self._get_or_create(name=name)


class RequestQueueCollectionClientAsync(ResourceCollectionClientAsync):
    """Async sub-client for manipulating request queues."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the RequestQueueCollectionClientAsync with the passed arguments."""
        resource_path = kwargs.pop('resource_path', 'request-queues')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    @_make_async_docs(src=RequestQueueCollectionClient.list)
    async def list(
        self,
        *,
        unnamed: Optional[bool] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        desc: Optional[bool] = None,
    ) -> ListPage:
        return await self._list(unnamed=unnamed, limit=limit, offset=offset, desc=desc)

    @_make_async_docs(src=RequestQueueCollectionClient.get_or_create)
    async def get_or_create(self, *, name: Optional[str] = None) -> Dict:
        return await self._get_or_create(name=name)
