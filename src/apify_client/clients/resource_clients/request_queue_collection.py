from __future__ import annotations

from typing import TYPE_CHECKING, Any

from apify_shared.utils import ignore_docs

from apify_client.clients.base import ResourceCollectionClient, ResourceCollectionClientAsync

if TYPE_CHECKING:
    from apify_shared.models import ListPage


class RequestQueueCollectionClient(ResourceCollectionClient):
    """Sub-client for manipulating request queues."""

    @ignore_docs
    def __init__(self: RequestQueueCollectionClient, *args: Any, **kwargs: Any) -> None:
        """Initialize the RequestQueueCollectionClient with the passed arguments."""
        resource_path = kwargs.pop('resource_path', 'request-queues')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def list(
        self: RequestQueueCollectionClient,
        *,
        unnamed: bool | None = None,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
    ) -> ListPage[dict]:
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

    def get_or_create(self: RequestQueueCollectionClient, *, name: str | None = None) -> dict:
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

    @ignore_docs
    def __init__(self: RequestQueueCollectionClientAsync, *args: Any, **kwargs: Any) -> None:
        """Initialize the RequestQueueCollectionClientAsync with the passed arguments."""
        resource_path = kwargs.pop('resource_path', 'request-queues')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def list(
        self: RequestQueueCollectionClientAsync,
        *,
        unnamed: bool | None = None,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
    ) -> ListPage[dict]:
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
        return await self._list(unnamed=unnamed, limit=limit, offset=offset, desc=desc)

    async def get_or_create(self: RequestQueueCollectionClientAsync, *, name: str | None = None) -> dict:
        """Retrieve a named request queue, or create a new one when it doesn't exist.

        https://docs.apify.com/api/v2#/reference/request-queues/queue-collection/create-request-queue

        Args:
            name (str, optional): The name of the request queue to retrieve or create.

        Returns:
            dict: The retrieved or newly-created request queue.
        """
        return await self._get_or_create(name=name)
