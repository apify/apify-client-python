from __future__ import annotations

import asyncio
import math
import warnings
from collections.abc import Iterable
from queue import Queue
from typing import TYPE_CHECKING, Any, Literal

from more_itertools import constrained_batches

from apify_client._docs import docs_group
from apify_client._iterable_list_page import (
    _LazyTask,
    _min_for_limit_param,
    build_cursor_iterable_list_page,
    build_cursor_iterable_list_page_async,
)
from apify_client._models import RequestDeleteInput, RequestInput
from apify_client._models_generated import (
    AddedRequest,
    AddRequestResponse,
    BatchAddResponse,
    BatchAddResult,
    BatchDeleteResponse,
    BatchDeleteResult,
    HeadAndLockResponse,
    HeadResponse,
    ListOfRequestsResponse,
    LockedRequestQueueHead,
    ProlongRequestLockResponse,
    Request,
    RequestDraft,
    RequestLockInfo,
    RequestQueue,
    RequestQueueHead,
    RequestQueueResponse,
    RequestRegistration,
    RequestResponse,
    UnlockRequestsResponse,
    UnlockRequestsResult,
)
from apify_client._pagination_classes import (
    ListPageOfRequests,
    ListPageOfRequestsAsync,
    PageOfRequests,
)
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync
from apify_client._utils import catch_not_found_or_throw, response_to_dict, to_seconds
from apify_client.errors import ApifyApiError

if TYPE_CHECKING:
    from datetime import timedelta

    from apify_client._models_generated import GeneralAccess
    from apify_client._typeddicts import RequestDeleteInputDict, RequestInputDict
    from apify_client._typeddicts_generated import RequestDict
    from apify_client._types import Timeout

_RQ_MAX_REQUESTS_PER_BATCH = 25
_MAX_PAYLOAD_SIZE_BYTES = 9 * 1024 * 1024  # 9 MB
_SAFETY_BUFFER_PERCENT = 0.01 / 100  # 0.01%


@docs_group('Resource clients')
class RequestQueueClient(ResourceClient):
    """Sub-client for managing a specific request queue.

    Provides methods to manage a specific request queue, e.g. update it, delete it, or manage its requests. Obtain an
    instance via an appropriate method on the `ApifyClient` class.
    """

    def __init__(  # noqa: D417
        self,
        *,
        resource_id: str | None = None,
        resource_path: str = 'request-queues',
        client_key: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize a new instance.

        Args:
            client_key: A unique identifier of the client accessing the request queue.
        """
        super().__init__(
            resource_id=resource_id,
            resource_path=resource_path,
            **kwargs,
        )
        self.client_key = client_key

    def get(self, *, timeout: Timeout = 'short') -> RequestQueue | None:
        """Retrieve the request queue.

        https://docs.apify.com/api/v2#/reference/request-queues/queue/get-request-queue

        Args:
            timeout: Timeout for the API HTTP request.

        Returns:
            The retrieved request queue, or None, if it does not exist.
        """
        result = self._get(timeout=timeout)
        if result is None:
            return None
        return RequestQueueResponse.model_validate(result).data

    def update(
        self,
        *,
        name: str | None = None,
        general_access: GeneralAccess | None = None,
        timeout: Timeout = 'short',
    ) -> RequestQueue:
        """Update the request queue with specified fields.

        https://docs.apify.com/api/v2#/reference/request-queues/queue/update-request-queue

        Args:
            name: The new name for the request queue.
            general_access: Determines how others can access the request queue.
            timeout: Timeout for the API HTTP request.

        Returns:
            The updated request queue.
        """
        result = self._update(timeout=timeout, name=name, generalAccess=general_access)
        return RequestQueueResponse.model_validate(result).data

    def delete(self, *, timeout: Timeout = 'short') -> None:
        """Delete the request queue.

        https://docs.apify.com/api/v2#/reference/request-queues/queue/delete-request-queue

        Args:
            timeout: Timeout for the API HTTP request.
        """
        self._delete(timeout=timeout)

    def list_head(self, *, limit: int | None = None, timeout: Timeout = 'short') -> RequestQueueHead:
        """Retrieve a given number of requests from the beginning of the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/queue-head/get-head

        Args:
            limit: How many requests to retrieve.
            timeout: Timeout for the API HTTP request.

        Returns:
            The desired number of requests from the beginning of the queue.
        """
        request_params = self._build_params(limit=limit, clientKey=self.client_key)

        response = self._http_client.call(
            url=self._build_url('head'),
            method='GET',
            params=request_params,
            timeout=timeout,
        )

        result = response_to_dict(response)
        return HeadResponse.model_validate(result).data

    def list_and_lock_head(
        self,
        *,
        lock_duration: timedelta,
        limit: int | None = None,
        timeout: Timeout = 'medium',
    ) -> LockedRequestQueueHead:
        """Retrieve a given number of unlocked requests from the beginning of the queue and lock them for a given time.

        https://docs.apify.com/api/v2#/reference/request-queues/queue-head-with-locks/get-head-and-lock

        Args:
            lock_duration: How long the requests will be locked for.
            limit: How many requests to retrieve.
            timeout: Timeout for the API HTTP request.

        Returns:
            The desired number of locked requests from the beginning of the queue.
        """
        request_params = self._build_params(
            lockSecs=to_seconds(lock_duration, as_int=True),
            limit=limit,
            clientKey=self.client_key,
        )

        response = self._http_client.call(
            url=self._build_url('head/lock'),
            method='POST',
            params=request_params,
            timeout=timeout,
        )

        result = response_to_dict(response)
        return HeadAndLockResponse.model_validate(result).data

    def add_request(
        self,
        request: RequestInputDict | RequestInput,
        *,
        forefront: bool | None = None,
        timeout: Timeout = 'short',
    ) -> RequestRegistration:
        """Add a request to the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/request-collection/add-request

        Args:
            request: The request to add to the queue.
            forefront: Whether to add the request to the head or the end of the queue.
            timeout: Timeout for the API HTTP request.

        Returns:
            The added request.
        """
        if not isinstance(request, RequestInput):
            request = RequestInput.model_validate(request)

        request_params = self._build_params(forefront=forefront, clientKey=self.client_key)

        response = self._http_client.call(
            url=self._build_url('requests'),
            method='POST',
            json=request.model_dump(by_alias=True, exclude_none=True),
            params=request_params,
            timeout=timeout,
        )

        result = response_to_dict(response)
        return AddRequestResponse.model_validate(result).data

    def get_request(self, request_id: str, *, timeout: Timeout = 'short') -> Request | None:
        """Retrieve a request from the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/request/get-request

        Args:
            request_id: ID of the request to retrieve.
            timeout: Timeout for the API HTTP request.

        Returns:
            The retrieved request, or None, if it did not exist.
        """
        try:
            response = self._http_client.call(
                url=self._build_url(f'requests/{request_id}'),
                method='GET',
                params=self._build_params(),
                timeout=timeout,
            )
            result = response_to_dict(response)
            return RequestResponse.model_validate(result).data

        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

        return None

    def update_request(
        self,
        request: RequestDict | Request,
        *,
        forefront: bool | None = None,
        timeout: Timeout = 'medium',
    ) -> RequestRegistration:
        """Update a request in the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/request/update-request

        Args:
            request: The updated request.
            forefront: Whether to put the updated request in the beginning or the end of the queue.
            timeout: Timeout for the API HTTP request.

        Returns:
            The updated request.
        """
        if not isinstance(request, Request):
            request = Request.model_validate(request)

        request_params = self._build_params(forefront=forefront, clientKey=self.client_key)

        response = self._http_client.call(
            url=self._build_url(f'requests/{request.id}'),
            method='PUT',
            json=request.model_dump(by_alias=True, exclude_none=True),
            params=request_params,
            timeout=timeout,
        )

        result = response_to_dict(response)
        return AddRequestResponse.model_validate(result).data

    def delete_request(self, request_id: str, *, timeout: Timeout = 'short') -> None:
        """Delete a request from the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/request/delete-request

        Args:
            request_id: ID of the request to delete.
            timeout: Timeout for the API HTTP request.
        """
        request_params = self._build_params(
            clientKey=self.client_key,
        )

        self._http_client.call(
            url=self._build_url(f'requests/{request_id}'),
            method='DELETE',
            params=request_params,
            timeout=timeout,
        )

    def prolong_request_lock(
        self,
        request_id: str,
        *,
        forefront: bool | None = None,
        lock_duration: timedelta,
        timeout: Timeout = 'medium',
    ) -> RequestLockInfo | None:
        """Prolong the lock on a request.

        https://docs.apify.com/api/v2#/reference/request-queues/request-lock/prolong-request-lock

        Args:
            request_id: ID of the request to prolong the lock.
            forefront: Whether to put the request in the beginning or the end of the queue after lock expires.
            lock_duration: By how much to prolong the lock.
            timeout: Timeout for the API HTTP request.
        """
        request_params = self._build_params(
            clientKey=self.client_key,
            forefront=forefront,
            lockSecs=to_seconds(lock_duration, as_int=True),
        )

        response = self._http_client.call(
            url=self._build_url(f'requests/{request_id}/lock'),
            method='PUT',
            params=request_params,
            timeout=timeout,
        )

        result = response_to_dict(response)
        return ProlongRequestLockResponse.model_validate(result).data

    def delete_request_lock(
        self,
        request_id: str,
        *,
        forefront: bool | None = None,
        timeout: Timeout = 'short',
    ) -> None:
        """Delete the lock on a request.

        https://docs.apify.com/api/v2#/reference/request-queues/request-lock/delete-request-lock

        Args:
            request_id: ID of the request to delete the lock.
            forefront: Whether to put the request in the beginning or the end of the queue after the lock is deleted.
            timeout: Timeout for the API HTTP request.
        """
        request_params = self._build_params(clientKey=self.client_key, forefront=forefront)

        self._http_client.call(
            url=self._build_url(f'requests/{request_id}/lock'),
            method='DELETE',
            params=request_params,
            timeout=timeout,
        )

    def batch_add_requests(
        self,
        requests: list[RequestInput] | list[RequestInputDict],
        *,
        forefront: bool = False,
        max_parallel: int = 1,
        max_unprocessed_requests_retries: int | None = None,
        min_delay_between_unprocessed_requests_retries: timedelta | None = None,
        timeout: Timeout = 'medium',
    ) -> BatchAddResult:
        """Add requests to the request queue in batches.

        Requests are split into batches based on size and processed in parallel.

        https://docs.apify.com/api/v2#/reference/request-queues/batch-request-operations/add-requests

        Args:
            requests: List of requests to be added to the queue.
            forefront: Whether to add requests to the front of the queue.
            max_parallel: Specifies the maximum number of parallel tasks for API calls. This is only applicable
                to the async client. For the sync client, this value must be set to 1, as parallel execution
                is not supported.
            max_unprocessed_requests_retries: Deprecated argument. Will be removed in next major release.
            min_delay_between_unprocessed_requests_retries: Deprecated argument. Will be removed in next major release.
            timeout: Timeout for the API HTTP request.

        Returns:
            Result containing lists of processed and unprocessed requests.
        """
        if max_unprocessed_requests_retries:
            warnings.warn(
                '`max_unprocessed_requests_retries` is deprecated and not used anymore.',
                DeprecationWarning,
                stacklevel=2,
            )
        if min_delay_between_unprocessed_requests_retries:
            warnings.warn(
                '`min_delay_between_unprocessed_requests_retries` is deprecated and not used anymore.',
                DeprecationWarning,
                stacklevel=2,
            )

        if max_parallel != 1:
            raise NotImplementedError('max_parallel is only supported in async client')

        requests_as_dicts = [
            (r if isinstance(r, RequestInput) else RequestInput.model_validate(r)).model_dump(
                by_alias=True, exclude_none=True
            )
            for r in requests
        ]

        request_params = self._build_params(clientKey=self.client_key, forefront=forefront)

        # Compute the payload size limit to ensure it doesn't exceed the maximum allowed size.
        payload_size_limit_bytes = _MAX_PAYLOAD_SIZE_BYTES - math.ceil(_MAX_PAYLOAD_SIZE_BYTES * _SAFETY_BUFFER_PERCENT)

        # Split the requests into batches, constrained by the max payload size and max requests per batch.
        batches = constrained_batches(
            requests_as_dicts,
            max_size=payload_size_limit_bytes,
            max_count=_RQ_MAX_REQUESTS_PER_BATCH,
        )

        # Put the batches into the queue for processing.
        queue = Queue[Iterable[dict]]()

        for batch in batches:
            queue.put(batch)

        processed_requests = list[AddedRequest]()
        unprocessed_requests = list[RequestDraft]()

        # Process all batches in the queue sequentially.
        while not queue.empty():
            request_batch = queue.get()

            # Send the batch to the API.
            response = self._http_client.call(
                url=self._build_url('requests/batch'),
                method='POST',
                params=request_params,
                json=list(request_batch),
                timeout=timeout,
            )

            result = response_to_dict(response)
            batch_response = BatchAddResponse.model_validate(result)
            processed_requests.extend(batch_response.data.processed_requests)
            unprocessed_requests.extend(batch_response.data.unprocessed_requests)

        return BatchAddResponse.model_construct(
            data=BatchAddResult.model_construct(
                processed_requests=processed_requests,
                unprocessed_requests=unprocessed_requests,
            )
        ).data

    def batch_delete_requests(
        self,
        requests: list[RequestDeleteInput] | list[RequestDeleteInputDict],
        *,
        timeout: Timeout = 'short',
    ) -> BatchDeleteResult:
        """Delete given requests from the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/batch-request-operations/delete-requests

        Args:
            requests: List of the requests to delete.
            timeout: Timeout for the API HTTP request.
        """
        requests_as_dicts = [
            (r if isinstance(r, RequestDeleteInput) else RequestDeleteInput.model_validate(r)).model_dump(
                by_alias=True, exclude_none=True
            )
            for r in requests
        ]

        request_params = self._build_params(clientKey=self.client_key)

        response = self._http_client.call(
            url=self._build_url('requests/batch'),
            method='DELETE',
            params=request_params,
            json=requests_as_dicts,
            timeout=timeout,
        )

        result = response_to_dict(response)
        return BatchDeleteResponse.model_validate(result).data

    def list_requests(
        self,
        *,
        limit: int | None = None,
        filter: list[Literal['pending', 'locked']] | None = None,  # noqa: A002
        cursor: str | None = None,
        exclusive_start_id: str | None = None,
        chunk_size: int | None = None,
        timeout: Timeout = 'medium',
    ) -> ListPageOfRequests:
        """List requests in the queue.

        The returned page also supports iteration: `for request in client.list_requests(...)` yields
        individual requests and transparently fetches further pages using the opaque `cursor`
        returned by the API.

        https://docs.apify.com/api/v2#/reference/request-queues/request-collection/list-requests

        Args:
            limit: How many requests to retrieve.
            filter: List of request states to use as a filter. Multiple values mean union of the given filters.
            cursor: A token returned in a previous API response, to continue listing the next page of requests.
            exclusive_start_id: (deprecated) All requests up to this one (including) are skipped from the result.
                Only applied to the first page fetched; subsequent pages during iteration use `cursor`.
            chunk_size: Maximum number of requests requested per API call when iterating. Only
                relevant when iterating across pages.
            timeout: Timeout for the API HTTP request.
            cursor: A token returned in previous API response, to continue listing next page of requests
            exclusive_start_id: (deprecated) All requests up to this one (including) are skipped from the result.
        """
        if exclusive_start_id and cursor:
            raise ValueError('Cannot use both `exclusive_start_id` and `cursor` for paginating requests.')

        if exclusive_start_id is not None:
            warnings.warn(
                '`exclusive_start_id` is deprecated for paginating requests. Use pagination using `cursor` instead.',
                DeprecationWarning,
                stacklevel=2,
            )

        def _callback(*, limit: int | None = None, cursor: str | None = None) -> PageOfRequests:
            # `exclusive_start_id` is honored only on the first page (when no cursor has been
            # produced by the server yet); subsequent pages rely on the opaque `cursor`.
            request_params = self._build_params(
                limit=limit,
                filter=','.join(filter) if filter else None,
                clientKey=self.client_key,
                exclusiveStartId=exclusive_start_id if cursor is None else None,
                cursor=cursor,
            )
            response = self._http_client.call(
                url=self._build_url('requests'),
                method='GET',
                params=request_params,
                timeout=timeout,
            )
            result = response_to_dict(response)
            data = ListOfRequestsResponse.model_validate(result).data
            with warnings.catch_warnings():
                # `exclusive_start_id` is deprecated on the API model; reading triggers a warning.
                warnings.simplefilter('ignore', DeprecationWarning)
                exclusive_start_id_value = data.exclusive_start_id
            return PageOfRequests(
                items=data.items,
                limit=data.limit,
                exclusive_start_id=exclusive_start_id_value,
                cursor=data.cursor,
                next_cursor=data.next_cursor,
            )

        first_limit = _min_for_limit_param(limit, chunk_size)
        first_page = _callback(limit=first_limit, cursor=cursor)
        get_iterator = build_cursor_iterable_list_page(
            _callback,
            first_page,
            cursor_param='cursor',
            limit=limit,
            chunk_size=chunk_size,
        )

        return ListPageOfRequests(
            _get_iterator=get_iterator,
            items=first_page.items,
            limit=first_page.limit,
            exclusive_start_id=first_page.exclusive_start_id,
            cursor=first_page.cursor,
            next_cursor=first_page.next_cursor,
        )

    def unlock_requests(self: RequestQueueClient, *, timeout: Timeout = 'long') -> UnlockRequestsResult:
        """Unlock all requests in the queue, which were locked by the same clientKey or from the same Actor run.

        https://docs.apify.com/api/v2#/reference/request-queues/request-collection/unlock-requests

        Args:
            timeout: Timeout for the API HTTP request.

        Returns:
            Result of the unlock operation containing the count of unlocked requests
        """
        request_params = self._build_params(clientKey=self.client_key)

        response = self._http_client.call(
            url=self._build_url('requests/unlock'),
            method='POST',
            params=request_params,
            timeout=timeout,
        )

        result = response_to_dict(response)
        return UnlockRequestsResponse.model_validate(result).data


@docs_group('Resource clients')
class RequestQueueClientAsync(ResourceClientAsync):
    """Sub-client for managing a specific request queue.

    Provides methods to manage a specific request queue, e.g. update it, delete it, or manage its requests. Obtain an
    instance via an appropriate method on the `ApifyClientAsync` class.
    """

    def __init__(  # noqa: D417
        self,
        *,
        resource_id: str | None = None,
        resource_path: str = 'request-queues',
        client_key: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize a new instance.

        Args:
            client_key: A unique identifier of the client accessing the request queue.
        """
        super().__init__(
            resource_id=resource_id,
            resource_path=resource_path,
            **kwargs,
        )
        self.client_key = client_key

    async def get(self, *, timeout: Timeout = 'short') -> RequestQueue | None:
        """Retrieve the request queue.

        https://docs.apify.com/api/v2#/reference/request-queues/queue/get-request-queue

        Args:
            timeout: Timeout for the API HTTP request.

        Returns:
            The retrieved request queue, or None, if it does not exist.
        """
        result = await self._get(timeout=timeout)
        if result is None:
            return None
        return RequestQueueResponse.model_validate(result).data

    async def update(
        self,
        *,
        name: str | None = None,
        general_access: GeneralAccess | None = None,
        timeout: Timeout = 'short',
    ) -> RequestQueue:
        """Update the request queue with specified fields.

        https://docs.apify.com/api/v2#/reference/request-queues/queue/update-request-queue

        Args:
            name: The new name for the request queue.
            general_access: Determines how others can access the request queue.
            timeout: Timeout for the API HTTP request.

        Returns:
            The updated request queue.
        """
        result = await self._update(timeout=timeout, name=name, generalAccess=general_access)
        return RequestQueueResponse.model_validate(result).data

    async def delete(self, *, timeout: Timeout = 'short') -> None:
        """Delete the request queue.

        https://docs.apify.com/api/v2#/reference/request-queues/queue/delete-request-queue

        Args:
            timeout: Timeout for the API HTTP request.
        """
        await self._delete(timeout=timeout)

    async def list_head(self, *, limit: int | None = None, timeout: Timeout = 'short') -> RequestQueueHead:
        """Retrieve a given number of requests from the beginning of the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/queue-head/get-head

        Args:
            limit: How many requests to retrieve.
            timeout: Timeout for the API HTTP request.

        Returns:
            The desired number of requests from the beginning of the queue.
        """
        request_params = self._build_params(limit=limit, clientKey=self.client_key)

        response = await self._http_client.call(
            url=self._build_url('head'),
            method='GET',
            params=request_params,
            timeout=timeout,
        )

        result = response_to_dict(response)
        return HeadResponse.model_validate(result).data

    async def list_and_lock_head(
        self,
        *,
        lock_duration: timedelta,
        limit: int | None = None,
        timeout: Timeout = 'medium',
    ) -> LockedRequestQueueHead:
        """Retrieve a given number of unlocked requests from the beginning of the queue and lock them for a given time.

        https://docs.apify.com/api/v2#/reference/request-queues/queue-head-with-locks/get-head-and-lock

        Args:
            lock_duration: How long the requests will be locked for.
            limit: How many requests to retrieve.
            timeout: Timeout for the API HTTP request.

        Returns:
            The desired number of locked requests from the beginning of the queue.
        """
        request_params = self._build_params(
            lockSecs=to_seconds(lock_duration, as_int=True),
            limit=limit,
            clientKey=self.client_key,
        )

        response = await self._http_client.call(
            url=self._build_url('head/lock'),
            method='POST',
            params=request_params,
            timeout=timeout,
        )

        result = response_to_dict(response)
        return HeadAndLockResponse.model_validate(result).data

    async def add_request(
        self,
        request: RequestInputDict | RequestInput,
        *,
        forefront: bool | None = None,
        timeout: Timeout = 'short',
    ) -> RequestRegistration:
        """Add a request to the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/request-collection/add-request

        Args:
            request: The request to add to the queue.
            forefront: Whether to add the request to the head or the end of the queue.
            timeout: Timeout for the API HTTP request.

        Returns:
            The added request.
        """
        if not isinstance(request, RequestInput):
            request = RequestInput.model_validate(request)

        request_params = self._build_params(forefront=forefront, clientKey=self.client_key)

        response = await self._http_client.call(
            url=self._build_url('requests'),
            method='POST',
            json=request.model_dump(by_alias=True, exclude_none=True),
            params=request_params,
            timeout=timeout,
        )

        result = response_to_dict(response)
        return AddRequestResponse.model_validate(result).data

    async def get_request(self, request_id: str, *, timeout: Timeout = 'short') -> Request | None:
        """Retrieve a request from the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/request/get-request

        Args:
            request_id: ID of the request to retrieve.
            timeout: Timeout for the API HTTP request.

        Returns:
            The retrieved request, or None, if it did not exist.
        """
        try:
            response = await self._http_client.call(
                url=self._build_url(f'requests/{request_id}'),
                method='GET',
                params=self._build_params(),
                timeout=timeout,
            )
            result = response_to_dict(response)
            return RequestResponse.model_validate(result).data
        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)
            return None

    async def update_request(
        self,
        request: RequestDict | Request,
        *,
        forefront: bool | None = None,
        timeout: Timeout = 'medium',
    ) -> RequestRegistration:
        """Update a request in the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/request/update-request

        Args:
            request: The updated request.
            forefront: Whether to put the updated request in the beginning or the end of the queue.
            timeout: Timeout for the API HTTP request.

        Returns:
            The updated request.
        """
        if not isinstance(request, Request):
            request = Request.model_validate(request)

        request_params = self._build_params(forefront=forefront, clientKey=self.client_key)

        response = await self._http_client.call(
            url=self._build_url(f'requests/{request.id}'),
            method='PUT',
            json=request.model_dump(by_alias=True, exclude_none=True),
            params=request_params,
            timeout=timeout,
        )

        result = response_to_dict(response)
        return AddRequestResponse.model_validate(result).data

    async def delete_request(self, request_id: str, *, timeout: Timeout = 'short') -> None:
        """Delete a request from the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/request/delete-request

        Args:
            request_id: ID of the request to delete.
            timeout: Timeout for the API HTTP request.
        """
        request_params = self._build_params(clientKey=self.client_key)

        await self._http_client.call(
            url=self._build_url(f'requests/{request_id}'),
            method='DELETE',
            params=request_params,
            timeout=timeout,
        )

    async def prolong_request_lock(
        self,
        request_id: str,
        *,
        forefront: bool | None = None,
        lock_duration: timedelta,
        timeout: Timeout = 'medium',
    ) -> RequestLockInfo | None:
        """Prolong the lock on a request.

        https://docs.apify.com/api/v2#/reference/request-queues/request-lock/prolong-request-lock

        Args:
            request_id: ID of the request to prolong the lock.
            forefront: Whether to put the request in the beginning or the end of the queue after lock expires.
            lock_duration: By how much to prolong the lock.
            timeout: Timeout for the API HTTP request.
        """
        request_params = self._build_params(
            clientKey=self.client_key,
            forefront=forefront,
            lockSecs=to_seconds(lock_duration, as_int=True),
        )

        response = await self._http_client.call(
            url=self._build_url(f'requests/{request_id}/lock'),
            method='PUT',
            params=request_params,
            timeout=timeout,
        )

        result = response_to_dict(response)
        return ProlongRequestLockResponse.model_validate(result).data

    async def delete_request_lock(
        self,
        request_id: str,
        *,
        forefront: bool | None = None,
        timeout: Timeout = 'short',
    ) -> None:
        """Delete the lock on a request.

        https://docs.apify.com/api/v2#/reference/request-queues/request-lock/delete-request-lock

        Args:
            request_id: ID of the request to delete the lock.
            forefront: Whether to put the request in the beginning or the end of the queue after the lock is deleted.
            timeout: Timeout for the API HTTP request.
        """
        request_params = self._build_params(clientKey=self.client_key, forefront=forefront)

        await self._http_client.call(
            url=self._build_url(f'requests/{request_id}/lock'),
            method='DELETE',
            params=request_params,
            timeout=timeout,
        )

    async def _batch_add_requests_worker(
        self,
        queue: asyncio.Queue[Iterable[dict]],
        request_params: dict,
        timeout: Timeout,
    ) -> BatchAddResponse:
        """Worker function to process a batch of requests.

        This worker will process batches from the queue.

        Return result containing lists of processed and unprocessed requests by the worker.
        """
        processed_requests = list[AddedRequest]()
        unprocessed_requests = list[RequestDraft]()

        while True:
            # Get the next batch from the queue.
            try:
                request_batch = await queue.get()
            except asyncio.CancelledError:
                break

            try:
                # Send the batch to the API.
                response = await self._http_client.call(
                    url=self._build_url('requests/batch'),
                    method='POST',
                    params=request_params,
                    json=list(request_batch),
                    timeout=timeout,
                )

                result = response_to_dict(response)
                batch_response = BatchAddResponse.model_validate(result)
                processed_requests.extend(batch_response.data.processed_requests)
                unprocessed_requests.extend(batch_response.data.unprocessed_requests)

            finally:
                # Mark the batch as done whether it succeeded or failed.
                queue.task_done()

        return BatchAddResponse.model_construct(
            data=BatchAddResult.model_construct(
                processed_requests=processed_requests,
                unprocessed_requests=unprocessed_requests,
            )
        )

    async def batch_add_requests(
        self,
        requests: list[RequestInput] | list[RequestInputDict],
        *,
        forefront: bool = False,
        max_parallel: int = 5,
        max_unprocessed_requests_retries: int | None = None,
        min_delay_between_unprocessed_requests_retries: timedelta | None = None,
        timeout: Timeout = 'medium',
    ) -> BatchAddResult:
        """Add requests to the request queue in batches.

        Requests are split into batches based on size and processed in parallel.

        https://docs.apify.com/api/v2#/reference/request-queues/batch-request-operations/add-requests

        Args:
            requests: List of requests to be added to the queue.
            forefront: Whether to add requests to the front of the queue.
            max_parallel: Specifies the maximum number of parallel tasks for API calls. This is only applicable
                to the async client. For the sync client, this value must be set to 1, as parallel execution
                is not supported.
            max_unprocessed_requests_retries: Deprecated argument. Will be removed in next major release.
            min_delay_between_unprocessed_requests_retries: Deprecated argument. Will be removed in next major release.
            timeout: Timeout for the API HTTP request.

        Returns:
            Result containing lists of processed and unprocessed requests.
        """
        if max_unprocessed_requests_retries:
            warnings.warn(
                '`max_unprocessed_requests_retries` is deprecated and not used anymore.',
                DeprecationWarning,
                stacklevel=2,
            )
        if min_delay_between_unprocessed_requests_retries:
            warnings.warn(
                '`min_delay_between_unprocessed_requests_retries` is deprecated and not used anymore.',
                DeprecationWarning,
                stacklevel=2,
            )

        requests_as_dicts = [
            (r if isinstance(r, RequestInput) else RequestInput.model_validate(r)).model_dump(
                by_alias=True, exclude_none=True
            )
            for r in requests
        ]

        asyncio_queue: asyncio.Queue[Iterable[dict]] = asyncio.Queue()
        request_params = self._build_params(clientKey=self.client_key, forefront=forefront)

        # Compute the payload size limit to ensure it doesn't exceed the maximum allowed size.
        payload_size_limit_bytes = _MAX_PAYLOAD_SIZE_BYTES - math.ceil(_MAX_PAYLOAD_SIZE_BYTES * _SAFETY_BUFFER_PERCENT)

        # Split the requests into batches, constrained by the max payload size and max requests per batch.
        batches = constrained_batches(
            requests_as_dicts,
            max_size=payload_size_limit_bytes,
            max_count=_RQ_MAX_REQUESTS_PER_BATCH,
        )

        for batch in batches:
            await asyncio_queue.put(batch)

        # Use TaskGroup for structured concurrency — automatic cleanup and error propagation.
        try:
            async with asyncio.TaskGroup() as tg:
                workers = [
                    tg.create_task(
                        self._batch_add_requests_worker(asyncio_queue, request_params, timeout),
                        name=f'batch_add_requests_worker_{i}',
                    )
                    for i in range(max_parallel)
                ]

                # Wait for all batches to be processed, then cancel idle workers.
                await asyncio_queue.join()
                for worker in workers:
                    worker.cancel()
        except ExceptionGroup as eg:
            # Re-raise the first worker exception directly to maintain backward-compatible error types.
            raise eg.exceptions[0] from None

        # Combine the results from all workers and return them.
        processed_requests = list[AddedRequest]()
        unprocessed_requests = list[RequestDraft]()

        for worker in workers:
            result = worker.result()
            processed_requests.extend(result.data.processed_requests)
            unprocessed_requests.extend(result.data.unprocessed_requests)

        return BatchAddResponse.model_construct(
            data=BatchAddResult.model_construct(
                processed_requests=processed_requests,
                unprocessed_requests=unprocessed_requests,
            )
        ).data

    async def batch_delete_requests(
        self,
        requests: list[RequestDeleteInput] | list[RequestDeleteInputDict],
        *,
        timeout: Timeout = 'short',
    ) -> BatchDeleteResult:
        """Delete given requests from the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/batch-request-operations/delete-requests

        Args:
            requests: List of the requests to delete.
            timeout: Timeout for the API HTTP request.
        """
        requests_as_dicts = [
            (r if isinstance(r, RequestDeleteInput) else RequestDeleteInput.model_validate(r)).model_dump(
                by_alias=True, exclude_none=True
            )
            for r in requests
        ]

        request_params = self._build_params(clientKey=self.client_key)

        response = await self._http_client.call(
            url=self._build_url('requests/batch'),
            method='DELETE',
            params=request_params,
            json=requests_as_dicts,
            timeout=timeout,
        )
        result = response_to_dict(response)
        return BatchDeleteResponse.model_validate(result).data

    def list_requests(
        self,
        *,
        limit: int | None = None,
        filter: list[Literal['pending', 'locked']] | None = None,  # noqa: A002
        cursor: str | None = None,
        exclusive_start_id: str | None = None,
        chunk_size: int | None = None,
        timeout: Timeout = 'medium',
    ) -> ListPageOfRequestsAsync:
        """List requests in the queue.

        The returned page also supports iteration: `async for request in client.list_requests(...)` yields
        individual requests and transparently fetches further pages using the opaque `cursor`
        returned by the API.

        https://docs.apify.com/api/v2#/reference/request-queues/request-collection/list-requests

        Args:
            limit: How many requests to retrieve.
            filter: List of request states to use as a filter. Multiple values mean union of the given filters.
            cursor: A token returned in a previous API response, to continue listing the next page of requests.
            exclusive_start_id: (deprecated) All requests up to this one (including) are skipped from the result.
                Only applied to the first page fetched; subsequent pages during iteration use `cursor`.
            chunk_size: Maximum number of requests requested per API call when iterating. Only
                relevant when iterating across pages.
            timeout: Timeout for the API HTTP request.
            cursor: A token returned in previous API response, to continue listing next page of requests
            exclusive_start_id: (deprecated) All requests up to this one (including) are skipped from the result.
        """
        if exclusive_start_id and cursor:
            raise ValueError('Cannot use both `exclusive_start_id` and `cursor` for paginating requests.')

        if exclusive_start_id is not None:
            warnings.warn(
                '`exclusive_start_id` is deprecated for paginating requests. Use pagination using `cursor` instead.',
                DeprecationWarning,
                stacklevel=2,
            )

        async def _callback(*, limit: int | None = None, cursor: str | None = None) -> PageOfRequests:
            # `exclusive_start_id` is honored only on the first page (when no cursor has been
            # produced by the server yet); subsequent pages rely on the opaque `cursor`.
            request_params = self._build_params(
                limit=limit,
                filter=','.join(filter) if filter else None,
                clientKey=self.client_key,
                exclusiveStartId=exclusive_start_id if cursor is None else None,
                cursor=cursor,
            )
            response = await self._http_client.call(
                url=self._build_url('requests'),
                method='GET',
                params=request_params,
                timeout=timeout,
            )
            result = response_to_dict(response)
            data = ListOfRequestsResponse.model_validate(result).data
            with warnings.catch_warnings():
                # `exclusive_start_id` is deprecated on the API model; reading triggers a warning.
                warnings.simplefilter('ignore', DeprecationWarning)
                exclusive_start_id_value = data.exclusive_start_id
            return PageOfRequests(
                items=data.items,
                limit=data.limit,
                exclusive_start_id=exclusive_start_id_value,
                cursor=data.cursor,
                next_cursor=data.next_cursor,
            )

        first_limit = _min_for_limit_param(limit, chunk_size)
        fetch_first_page = _LazyTask(_callback(limit=first_limit, cursor=cursor))
        get_async_iterator = build_cursor_iterable_list_page_async(
            _callback,
            fetch_first_page,
            cursor_param='cursor',
            limit=limit,
            chunk_size=chunk_size,
        )

        return ListPageOfRequestsAsync(
            _awaitable_first_page=fetch_first_page,
            _get_async_iterator=get_async_iterator,
        )

    async def unlock_requests(
        self: RequestQueueClientAsync,
        *,
        timeout: Timeout = 'long',
    ) -> UnlockRequestsResult:
        """Unlock all requests in the queue, which were locked by the same clientKey or from the same Actor run.

        https://docs.apify.com/api/v2#/reference/request-queues/request-collection/unlock-requests

        Args:
            timeout: Timeout for the API HTTP request.

        Returns:
            Result of the unlock operation containing the count of unlocked requests
        """
        request_params = self._build_params(clientKey=self.client_key)

        response = await self._http_client.call(
            url=self._build_url('requests/unlock'),
            method='POST',
            params=request_params,
            timeout=timeout,
        )

        result = response_to_dict(response)
        return UnlockRequestsResponse.model_validate(result).data
