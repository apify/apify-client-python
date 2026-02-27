from __future__ import annotations

from typing import Any

from apify_client._docs import docs_group
from apify_client._models import (
    ListOfRequestQueues,
    ListOfRequestQueuesResponse,
    RequestQueue,
    RequestQueueResponse,
)
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync


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
    ) -> ListOfRequestQueues:
        """List the available request queues.

        https://docs.apify.com/api/v2#/reference/request-queues/queue-collection/get-list-of-request-queues

        Args:
            unnamed: Whether to include unnamed request queues in the list.
            limit: How many request queues to retrieve.
            offset: What request queue to include as first when retrieving the list.
            desc: Whether to sort therequest queues in descending order based on their modification date.

        Returns:
            The list of available request queues matching the specified filters.
        """
        result = self._list(unnamed=unnamed, limit=limit, offset=offset, desc=desc)
        return ListOfRequestQueuesResponse.model_validate(result).data

    def get_or_create(self, *, name: str | None = None) -> RequestQueue:
        """Retrieve a named request queue, or create a new one when it doesn't exist.

        https://docs.apify.com/api/v2#/reference/request-queues/queue-collection/create-request-queue

        Args:
            name: The name of the request queue to retrieve or create.

        Returns:
            The retrieved or newly-created request queue.
        """
        result = self._get_or_create(name=name)
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
    ) -> ListOfRequestQueues:
        """List the available request queues.

        https://docs.apify.com/api/v2#/reference/request-queues/queue-collection/get-list-of-request-queues

        Args:
            unnamed: Whether to include unnamed request queues in the list.
            limit: How many request queues to retrieve.
            offset: What request queue to include as first when retrieving the list.
            desc: Whether to sort therequest queues in descending order based on their modification date.

        Returns:
            The list of available request queues matching the specified filters.
        """
        result = await self._list(unnamed=unnamed, limit=limit, offset=offset, desc=desc)
        return ListOfRequestQueuesResponse.model_validate(result).data

    async def get_or_create(self, *, name: str | None = None) -> RequestQueue:
        """Retrieve a named request queue, or create a new one when it doesn't exist.

        https://docs.apify.com/api/v2#/reference/request-queues/queue-collection/create-request-queue

        Args:
            name: The name of the request queue to retrieve or create.

        Returns:
            The retrieved or newly-created request queue.
        """
        result = await self._get_or_create(name=name)
        return RequestQueueResponse.model_validate(result).data
