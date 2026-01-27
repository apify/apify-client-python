from __future__ import annotations

from typing import Any

from apify_client._models import (
    CreateRequestQueueResponse,
    GetListOfRequestQueuesResponse,
    ListOfRequestQueues,
    RequestQueue,
)
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync
from apify_client._utils import response_to_dict


class RequestQueueCollectionClient(ResourceClient):
    """Sub-client for manipulating request queues."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'request-queues')
        super().__init__(*args, resource_path=resource_path, **kwargs)

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
        response = self.http_client.call(
            url=self._url(),
            method='GET',
            params=self._build_params(unnamed=unnamed, limit=limit, offset=offset, desc=desc),
        )
        response_as_dict = response_to_dict(response)
        return GetListOfRequestQueuesResponse.model_validate(response_as_dict).data

    def get_or_create(self, *, name: str | None = None) -> RequestQueue:
        """Retrieve a named request queue, or create a new one when it doesn't exist.

        https://docs.apify.com/api/v2#/reference/request-queues/queue-collection/create-request-queue

        Args:
            name: The name of the request queue to retrieve or create.

        Returns:
            The retrieved or newly-created request queue.
        """
        response = self.http_client.call(
            url=self._url(),
            method='POST',
            params=self._build_params(name=name),
        )
        result = response_to_dict(response)
        return CreateRequestQueueResponse.model_validate(result).data


class RequestQueueCollectionClientAsync(ResourceClientAsync):
    """Async sub-client for manipulating request queues."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'request-queues')
        super().__init__(*args, resource_path=resource_path, **kwargs)

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
        response = await self.http_client.call(
            url=self._url(),
            method='GET',
            params=self._build_params(unnamed=unnamed, limit=limit, offset=offset, desc=desc),
        )
        response_as_dict = response_to_dict(response)
        return GetListOfRequestQueuesResponse.model_validate(response_as_dict).data

    async def get_or_create(self, *, name: str | None = None) -> RequestQueue:
        """Retrieve a named request queue, or create a new one when it doesn't exist.

        https://docs.apify.com/api/v2#/reference/request-queues/queue-collection/create-request-queue

        Args:
            name: The name of the request queue to retrieve or create.

        Returns:
            The retrieved or newly-created request queue.
        """
        response = await self.http_client.call(
            url=self._url(),
            method='POST',
            params=self._build_params(name=name),
        )
        result = response_to_dict(response)
        return CreateRequestQueueResponse.model_validate(result).data
