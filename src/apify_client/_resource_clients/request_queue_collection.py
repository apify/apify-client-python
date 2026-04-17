from __future__ import annotations

from typing import TYPE_CHECKING, Any

from apify_client._docs import docs_group
from apify_client._iterable_list_page import (
    IterableListPage,
    IterableListPageAsync,
    build_iterable_list_page,
    build_iterable_list_page_async,
)
from apify_client._models import (
    ListOfRequestQueues,
    ListOfRequestQueuesResponse,
    RequestQueue,
    RequestQueueResponse,
)
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync

if TYPE_CHECKING:
    from apify_client._models import RequestQueueShort
    from apify_client._types import StorageOwnership, Timeout


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
    ) -> IterableListPage[RequestQueueShort]:
        """List the available request queues.

        The returned page also supports iteration: `for item in client.list(...)` yields individual
        request queues and transparently fetches further pages from the API.

        https://docs.apify.com/api/v2#/reference/request-queues/queue-collection/get-list-of-request-queues

        Args:
            unnamed: Whether to include unnamed request queues in the list.
            limit: How many request queues to retrieve.
            offset: What request queue to include as first when retrieving the list.
            desc: Whether to sort the request queues in descending order based on their modification date.
            ownership: Filter by ownership. 'ownedByMe' returns only user's own request queues,
                'sharedWithMe' returns only request queues shared with the user.
            timeout: Timeout for the API HTTP request.

        Returns:
            The list of available request queues matching the specified filters.
        """

        def _callback(**kwargs: Any) -> ListOfRequestQueues:
            result = self._list(timeout=timeout, unnamed=unnamed, ownership=ownership, **kwargs)
            return ListOfRequestQueuesResponse.model_validate(result).data

        return build_iterable_list_page(_callback, limit=limit, offset=offset, desc=desc)

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

    def list(
        self,
        *,
        unnamed: bool | None = None,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
        ownership: StorageOwnership | None = None,
        timeout: Timeout = 'medium',
    ) -> IterableListPageAsync[RequestQueueShort]:
        """List the available request queues.

        The returned page also supports iteration: `for item in client.list(...)` yields individual
        request queues and transparently fetches further pages from the API.

        https://docs.apify.com/api/v2#/reference/request-queues/queue-collection/get-list-of-request-queues

        Args:
            unnamed: Whether to include unnamed request queues in the list.
            limit: How many request queues to retrieve.
            offset: What request queue to include as first when retrieving the list.
            desc: Whether to sort the request queues in descending order based on their modification date.
            ownership: Filter by ownership. 'ownedByMe' returns only user's own request queues,
                'sharedWithMe' returns only request queues shared with the user.
            timeout: Timeout for the API HTTP request.

        Returns:
            The list of available request queues matching the specified filters.
        """

        async def _callback(**kwargs: Any) -> ListOfRequestQueues:
            result = await self._list(timeout=timeout, unnamed=unnamed, ownership=ownership, **kwargs)
            return ListOfRequestQueuesResponse.model_validate(result).data

        return build_iterable_list_page_async(_callback, limit=limit, offset=offset, desc=desc)

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
