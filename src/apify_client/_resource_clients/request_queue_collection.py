from __future__ import annotations

from typing import TYPE_CHECKING, Any

from apify_client._docs import docs_group
from apify_client._models import (
    ListOfRequestQueues,
    ListOfRequestQueuesResponse,
    RequestQueue,
    RequestQueueResponse,
)
from apify_client._pagination import get_items_iterator, get_items_iterator_async
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator

    from apify_client._literals import StorageOwnership
    from apify_client._models import RequestQueueShort
    from apify_client.types import Timeout


@docs_group('Resource clients')
class RequestQueueCollectionClient(ResourceClient):
    """Sub-client for the request queue collection.

    Provides methods to manage the request queue collection, e.g. list or create request queues. Obtain an instance
    via an appropriate method on the `ApifyClient` class.
    """

    def __init__(
        self,
        *,
        resource_path: str = 'request-queues',
        **kwargs: Any,
    ) -> None:
        super().__init__(
            resource_path=resource_path,
            **kwargs,
        )

    def list(
        self,
        *,
        unnamed: bool | None = None,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
        ownership: StorageOwnership | None = None,
        timeout: Timeout = 'medium',
    ) -> ListOfRequestQueues:
        """List the available request queues.

        https://docs.apify.com/api/v2#/reference/request-queues/queue-collection/get-list-of-request-queues

        Args:
            unnamed: Whether to include unnamed request queues in the list.
            limit: How many request queues to retrieve.
            offset: What request queue to include as first when retrieving the list.
            desc: Whether to sort the request queues in descending order based on their modification date.
            ownership: Filter by ownership. `'ownedByMe'` returns only user's own request queues,
                `'sharedWithMe'` returns only request queues shared with the user.
            timeout: Timeout for the API HTTP request.

        Returns:
            The list of available request queues matching the specified filters.
        """
        result = self._list(
            timeout=timeout,
            unnamed=unnamed,
            limit=limit,
            offset=offset,
            desc=desc,
            ownership=ownership,
        )
        return ListOfRequestQueuesResponse.model_validate(result).data

    def iterate(
        self,
        *,
        unnamed: bool | None = None,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
        ownership: StorageOwnership | None = None,
        timeout: Timeout = 'medium',
    ) -> Iterator[RequestQueueShort]:
        """Iterate over the available request queues.

        Simple `list` does only one API call, possibly not listing all items matching the criteria. This method
        returns an iterator that is capable of making multiple API calls to retrieve all items matching the criteria.

        https://docs.apify.com/api/v2#/reference/request-queues/queue-collection/get-list-of-request-queues

        Args:
            unnamed: Whether to include unnamed request queues in the list.
            limit: How many request queues to retrieve.
            offset: What request queue to include as first when retrieving the list.
            desc: Whether to sort the request queues in descending order based on their modification date.
            ownership: Filter by ownership. 'ownedByMe' returns only user's own request queues,
                'sharedWithMe' returns only request queues shared with the user.
            timeout: Timeout for the API HTTP request.

        Yields:
            The available request queues matching the specified filters.
        """

        def _callback(*, limit: int | None = None, offset: int | None = None) -> ListOfRequestQueues:
            return self.list(
                unnamed=unnamed, limit=limit, offset=offset, desc=desc, ownership=ownership, timeout=timeout
            )

        return get_items_iterator(_callback, limit=limit, offset=offset)

    def get_or_create(
        self,
        *,
        name: str | None = None,
        timeout: Timeout = 'short',
    ) -> RequestQueue:
        """Retrieve a named request queue, or create a new one when it doesn't exist.

        https://docs.apify.com/api/v2#/reference/request-queues/queue-collection/create-request-queue

        Args:
            name: The name of the request queue to retrieve or create.
            timeout: Timeout for the API HTTP request.

        Returns:
            The retrieved or newly-created request queue.
        """
        result = self._get_or_create(timeout=timeout, name=name)
        return RequestQueueResponse.model_validate(result).data


@docs_group('Resource clients')
class RequestQueueCollectionClientAsync(ResourceClientAsync):
    """Sub-client for the request queue collection.

    Provides methods to manage the request queue collection, e.g. list or create request queues. Obtain an instance
    via an appropriate method on the `ApifyClientAsync` class.
    """

    def __init__(
        self,
        *,
        resource_path: str = 'request-queues',
        **kwargs: Any,
    ) -> None:
        super().__init__(
            resource_path=resource_path,
            **kwargs,
        )

    async def list(
        self,
        *,
        unnamed: bool | None = None,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
        ownership: StorageOwnership | None = None,
        timeout: Timeout = 'medium',
    ) -> ListOfRequestQueues:
        """List the available request queues.

        https://docs.apify.com/api/v2#/reference/request-queues/queue-collection/get-list-of-request-queues

        Args:
            unnamed: Whether to include unnamed request queues in the list.
            limit: How many request queues to retrieve.
            offset: What request queue to include as first when retrieving the list.
            desc: Whether to sort the request queues in descending order based on their modification date.
            ownership: Filter by ownership. `'ownedByMe'` returns only user's own request queues,
                `'sharedWithMe'` returns only request queues shared with the user.
            timeout: Timeout for the API HTTP request.

        Returns:
            The list of available request queues matching the specified filters.
        """
        result = await self._list(
            timeout=timeout,
            unnamed=unnamed,
            limit=limit,
            offset=offset,
            desc=desc,
            ownership=ownership,
        )
        return ListOfRequestQueuesResponse.model_validate(result).data

    def iterate(
        self,
        *,
        unnamed: bool | None = None,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
        ownership: StorageOwnership | None = None,
        timeout: Timeout = 'medium',
    ) -> AsyncIterator[RequestQueueShort]:
        """Iterate over the available request queues.

        Simple `list` does only one API call, possibly not listing all items matching the criteria. This method
        returns an iterator that is capable of making multiple API calls to retrieve all items matching the criteria.

        https://docs.apify.com/api/v2#/reference/request-queues/queue-collection/get-list-of-request-queues

        Args:
            unnamed: Whether to include unnamed request queues in the list.
            limit: How many request queues to retrieve.
            offset: What request queue to include as first when retrieving the list.
            desc: Whether to sort the request queues in descending order based on their modification date.
            ownership: Filter by ownership. 'ownedByMe' returns only user's own request queues,
                'sharedWithMe' returns only request queues shared with the user.
            timeout: Timeout for the API HTTP request.

        Yields:
            The available request queues matching the specified filters.
        """

        async def _callback(*, limit: int | None = None, offset: int | None = None) -> ListOfRequestQueues:
            return await self.list(
                unnamed=unnamed, limit=limit, offset=offset, desc=desc, ownership=ownership, timeout=timeout
            )

        return get_items_iterator_async(_callback, limit=limit, offset=offset)

    async def get_or_create(
        self,
        *,
        name: str | None = None,
        timeout: Timeout = 'short',
    ) -> RequestQueue:
        """Retrieve a named request queue, or create a new one when it doesn't exist.

        https://docs.apify.com/api/v2#/reference/request-queues/queue-collection/create-request-queue

        Args:
            name: The name of the request queue to retrieve or create.
            timeout: Timeout for the API HTTP request.

        Returns:
            The retrieved or newly-created request queue.
        """
        result = await self._get_or_create(timeout=timeout, name=name)
        return RequestQueueResponse.model_validate(result).data
