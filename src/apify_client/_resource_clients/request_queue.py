from __future__ import annotations

import asyncio
import json
import math
import random
import time
from collections.abc import Iterable
from datetime import timedelta
from queue import Queue
from typing import TYPE_CHECKING, Any, Literal, NamedTuple

from more_itertools import constrained_batches

from apify_client._consts import (
    DEFAULT_MIN_DELAY_BETWEEN_UNPROCESSED_REQUESTS_RETRIES,
    DEFAULT_UNPROCESSED_RETRIES_BATCH_ADD_REQUESTS,
)
from apify_client._docs import docs_group
from apify_client._logging import logger
from apify_client._models import (
    AddedRequest,
    AddRequestResponse,
    BatchAddResponse,
    BatchAddResult,
    BatchDeleteResponse,
    BatchDeleteResult,
    ListOfRequests,
    ListOfRequestsResponse,
    LockedRequestQueueHead,
    LockedRequestQueueHeadResponse,
    ProlongRequestLockResponse,
    RequestLockInfo,
    RequestQueueHead,
    RequestQueueHeadResponse,
    RequestQueueResource,
    RequestQueueResponse,
    RequestRegistration,
    RequestResource,
    RequestResponse,
    RequestToDelete,
    RequestWithoutId,
    UnlockRequestsResponse,
    UnlockRequestsResult,
    UnprocessedRequest,
)
from apify_client._pagination import DEFAULT_CHUNK_SIZE, get_cursor_iterator, get_cursor_iterator_async
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync
from apify_client._utils.errors import catch_not_found_or_throw
from apify_client._utils.http import response_to_dict, to_path_segment
from apify_client._utils.time import to_seconds
from apify_client.errors import ApifyApiError

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator

    from apify_client._literals import GeneralAccess
    from apify_client._typeddicts import (
        RequestResourceCamelDict,
        RequestResourceDict,
        RequestToDeleteCamelDict,
        RequestToDeleteDict,
        RequestWithoutIdCamelDict,
        RequestWithoutIdDict,
    )
    from apify_client.types import QueryParams, Timeout

_RQ_MAX_REQUESTS_PER_BATCH = 25
"""Maximum number of requests the API accepts in a single batch call."""

_MAX_PAYLOAD_SIZE_BYTES = 9 * 1024 * 1024
"""Maximum payload size (9 MB) the API accepts for a single batch call."""

_SAFETY_BUFFER_PERCENT = 0.01 / 100
"""Safety margin (0.01%) deducted from the maximum payload size when splitting requests into batches."""


def _serialize_requests(
    requests: list[RequestWithoutId] | list[RequestWithoutIdDict] | list[RequestWithoutIdCamelDict],
) -> list[tuple[str, bytes]]:
    """Validate requests and serialize each one into `(unique_key, json_bytes)` for batch upload.

    Each request is serialized exactly once: the same bytes are measured when splitting requests into batches and
    then assembled into the request body, so batch sizes are computed on exactly the bytes that get sent. Pairing each
    payload with its validated `unique_key` lets unprocessed-request retry rounds reassemble only the remaining items
    without re-serializing or decoding payloads. Uses the same `json.dumps` options as
    `HttpClientBase._prepare_request_call` to keep the wire format consistent with other endpoints.
    """
    serialized = list[tuple[str, bytes]]()
    for request in requests:
        validated = request if isinstance(request, RequestWithoutId) else RequestWithoutId.model_validate(request)
        payload = json.dumps(
            validated.model_dump(mode='json', by_alias=True, exclude_none=True, fallback=str),
            ensure_ascii=False,
            allow_nan=False,
            default=str,
        ).encode('utf-8')
        serialized.append((validated.unique_key, payload))
    return serialized


def _validate_batch_retry_params(
    *,
    max_unprocessed_requests_retries: int,
    min_delay_between_unprocessed_requests_retries: timedelta,
) -> None:
    """Validate retry count and minimum backoff delay for `batch_add_requests`."""
    if max_unprocessed_requests_retries < 0:
        raise ValueError(
            f'max_unprocessed_requests_retries must be non-negative, got {max_unprocessed_requests_retries}'
        )
    if min_delay_between_unprocessed_requests_retries < timedelta(0):
        raise ValueError(
            'min_delay_between_unprocessed_requests_retries must be non-negative, '
            f'got {min_delay_between_unprocessed_requests_retries}'
        )


def _compute_retry_delay_seconds(attempt: int, min_delay: timedelta) -> float:
    """Compute exponential backoff delay with jitter for an unprocessed-requests retry round."""
    return random.uniform(1.0, 2.0) * (2**attempt) * to_seconds(min_delay)


class _BatchAttemptResult(NamedTuple):
    """Result of evaluating a single `batch_add_requests` attempt."""

    processed_requests: list[AddedRequest]
    unprocessed_requests: list[UnprocessedRequest]
    remaining_items: list[tuple[str, bytes]]
    processed_unique_keys: frozenset[str]


def _extract_batch_attempt_result(
    *,
    batch_items: list[tuple[str, bytes]],
    batch_response: BatchAddResponse,
    already_processed_keys: frozenset[str],
) -> _BatchAttemptResult:
    """Compute newly processed requests, unprocessed requests, and remaining items to retry."""
    new_processed = batch_response.data.processed_requests
    unprocessed = batch_response.data.unprocessed_requests
    if not unprocessed:
        return _BatchAttemptResult(
            processed_requests=new_processed,
            unprocessed_requests=unprocessed,
            remaining_items=[],
            processed_unique_keys=already_processed_keys,
        )
    updated_keys = already_processed_keys | {req.unique_key for req in new_processed}
    remaining = [item for item in batch_items if item[0] not in updated_keys]
    return _BatchAttemptResult(
        processed_requests=new_processed,
        unprocessed_requests=unprocessed,
        remaining_items=remaining,
        processed_unique_keys=updated_keys,
    )


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

    def get(self, *, timeout: Timeout = 'short') -> RequestQueueResource | None:
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
        title: str | None = None,
        general_access: GeneralAccess | None = None,
        timeout: Timeout = 'short',
    ) -> RequestQueueResource:
        """Update the request queue with specified fields.

        https://docs.apify.com/api/v2#/reference/request-queues/queue/update-request-queue

        Args:
            name: The new name for the request queue.
            title: The new title for the request queue.
            general_access: Determines how others can access the request queue.
            timeout: Timeout for the API HTTP request.

        Returns:
            The updated request queue.
        """
        result = self._update(timeout=timeout, name=name, title=title, generalAccess=general_access)
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
        return RequestQueueHeadResponse.model_validate(result).data

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
        return LockedRequestQueueHeadResponse.model_validate(result).data

    def add_request(
        self,
        request: RequestWithoutIdDict | RequestWithoutIdCamelDict | RequestWithoutId,
        *,
        forefront: bool | None = None,
        timeout: Timeout = 'short',
    ) -> RequestRegistration:
        """Add a request to the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/request-collection/add-request

        Args:
            request: The request to add to the queue. Must carry a `unique_key` and a `url`.
            forefront: Whether to add the request to the head or the end of the queue.
            timeout: Timeout for the API HTTP request.

        Returns:
            The added request.
        """
        if not isinstance(request, RequestWithoutId):
            request = RequestWithoutId.model_validate(request)

        request_params = self._build_params(forefront=forefront, clientKey=self.client_key)

        response = self._http_client.call(
            url=self._build_url('requests'),
            method='POST',
            json=request.model_dump(mode='json', by_alias=True, exclude_none=True, fallback=str),
            params=request_params,
            timeout=timeout,
        )

        result = response_to_dict(response)
        return AddRequestResponse.model_validate(result).data

    def get_request(self, request_id: str, *, timeout: Timeout = 'short') -> RequestResource | None:
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
                url=self._build_url(f'requests/{to_path_segment(request_id)}'),
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
        request: RequestResourceDict | RequestResourceCamelDict | RequestResource,
        *,
        forefront: bool | None = None,
        timeout: Timeout = 'medium',
    ) -> RequestRegistration:
        """Update a request in the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/request/update-request

        Args:
            request: The updated request. It must carry the ID of the request to update.
            forefront: Whether to put the updated request in the beginning or the end of the queue.
            timeout: Timeout for the API HTTP request.

        Returns:
            The updated request.

        Raises:
            ValueError: If the request carries no ID.
        """
        if not isinstance(request, RequestResource):
            request = RequestResource.model_validate(request)

        if request.id is None:
            raise ValueError('The request to update must have an ID.')

        request_params = self._build_params(forefront=forefront, clientKey=self.client_key)

        response = self._http_client.call(
            url=self._build_url(f'requests/{to_path_segment(request.id)}'),
            method='PUT',
            json=request.model_dump(mode='json', by_alias=True, exclude_none=True, fallback=str),
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
            url=self._build_url(f'requests/{to_path_segment(request_id)}'),
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
            url=self._build_url(f'requests/{to_path_segment(request_id)}/lock'),
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
            url=self._build_url(f'requests/{to_path_segment(request_id)}/lock'),
            method='DELETE',
            params=request_params,
            timeout=timeout,
        )

    def batch_add_requests(
        self,
        requests: list[RequestWithoutId] | list[RequestWithoutIdDict] | list[RequestWithoutIdCamelDict],
        *,
        forefront: bool = False,
        max_parallel: int = 1,
        max_unprocessed_requests_retries: int = DEFAULT_UNPROCESSED_RETRIES_BATCH_ADD_REQUESTS,
        min_delay_between_unprocessed_requests_retries: timedelta = (
            DEFAULT_MIN_DELAY_BETWEEN_UNPROCESSED_REQUESTS_RETRIES
        ),
        timeout: Timeout = 'medium',
    ) -> BatchAddResult:
        """Add requests to the request queue in batches.

        Requests are split into batches based on size and processed in parallel. Any requests reported as unprocessed
        by the API are retried with exponential backoff.

        https://docs.apify.com/api/v2#/reference/request-queues/batch-request-operations/add-requests

        Args:
            requests: List of requests to be added to the queue. Each must carry a `unique_key` and a `url`.
            forefront: Whether to add requests to the front of the queue.
            max_parallel: Specifies the maximum number of parallel tasks for API calls. This is only applicable
                to the async client. For the sync client, this value must be set to 1, as parallel execution
                is not supported.
            max_unprocessed_requests_retries: Maximum number of retry attempts for requests returned as unprocessed
                by the API.
            min_delay_between_unprocessed_requests_retries: Minimum delay before retrying unprocessed requests.
            timeout: Timeout for the API HTTP request.

        Returns:
            Result containing lists of processed and unprocessed requests.
        """
        if max_parallel != 1:
            raise NotImplementedError('max_parallel is only supported in async client')
        _validate_batch_retry_params(
            max_unprocessed_requests_retries=max_unprocessed_requests_retries,
            min_delay_between_unprocessed_requests_retries=min_delay_between_unprocessed_requests_retries,
        )

        # Validate the requests and serialize each of them into `(unique_key, json_bytes)`.
        serialized_requests = _serialize_requests(requests)

        # Build the query parameters shared by all the batch API calls.
        request_params = self._build_params(clientKey=self.client_key, forefront=forefront)

        # Compute the payload size limit to ensure it doesn't exceed the maximum allowed size.
        payload_size_limit_bytes = _MAX_PAYLOAD_SIZE_BYTES - math.ceil(_MAX_PAYLOAD_SIZE_BYTES * _SAFETY_BUFFER_PERCENT)

        # Split the requests into batches by payload size (counting commas and brackets) and max requests per batch.
        batches = constrained_batches(
            serialized_requests,
            max_size=payload_size_limit_bytes - len(b'[]'),
            max_count=_RQ_MAX_REQUESTS_PER_BATCH,
            get_len=lambda item: len(item[1]) + len(b','),
            strict=False,
        )

        # Put the batches into the queue for processing.
        batch_queue = Queue[Iterable[tuple[str, bytes]]]()

        for batch in batches:
            batch_queue.put(batch)

        processed_requests = list[AddedRequest]()
        unprocessed_requests = list[UnprocessedRequest]()

        # Process all batches in the queue sequentially.
        while not batch_queue.empty():
            batch_items = list(batch_queue.get())
            remaining_items = batch_items
            processed_unique_keys = frozenset[str]()
            batch_processed_requests = list[AddedRequest]()
            batch_unprocessed_requests = list[UnprocessedRequest]()

            for attempt in range(1 + max_unprocessed_requests_retries):
                try:
                    response = self._http_client.call(
                        url=self._build_url('requests/batch'),
                        method='POST',
                        headers={'content-type': 'application/json'},
                        params=request_params,
                        data=b'[' + b','.join(payload for _, payload in remaining_items) + b']',
                        timeout=timeout,
                    )
                    result = response_to_dict(response)
                    batch_response = BatchAddResponse.model_validate(result)
                except Exception:
                    if attempt == 0:
                        raise
                    logger.exception(
                        'Failed to retry unprocessed requests in request queue batch; returning partial result.'
                    )
                    break

                attempt_result = _extract_batch_attempt_result(
                    batch_items=batch_items,
                    batch_response=batch_response,
                    already_processed_keys=processed_unique_keys,
                )
                batch_processed_requests.extend(attempt_result.processed_requests)
                batch_unprocessed_requests = attempt_result.unprocessed_requests
                remaining_items = attempt_result.remaining_items
                processed_unique_keys = attempt_result.processed_unique_keys
                if batch_unprocessed_requests:
                    self._http_client.stats.add_rate_limit_error(attempt + 1)
                if not remaining_items:
                    break

                if attempt < max_unprocessed_requests_retries:
                    time.sleep(_compute_retry_delay_seconds(attempt, min_delay_between_unprocessed_requests_retries))

            processed_requests.extend(batch_processed_requests)
            unprocessed_requests.extend(batch_unprocessed_requests)

        return BatchAddResponse.model_construct(
            data=BatchAddResult.model_construct(
                processed_requests=processed_requests,
                unprocessed_requests=unprocessed_requests,
            )
        ).data

    def batch_delete_requests(
        self,
        requests: list[RequestToDelete] | list[RequestToDeleteDict] | list[RequestToDeleteCamelDict],
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
            (
                request
                if isinstance(request, RequestToDelete)
                else RequestToDelete.model_validate(
                    request,
                )
            ).root.model_dump(mode='json', by_alias=True, exclude_none=True, fallback=str)
            for request in requests
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
        timeout: Timeout = 'medium',
        cursor: str | None = None,
    ) -> ListOfRequests:
        """List requests in the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/request-collection/list-requests

        Args:
            limit: How many requests to retrieve.
            filter: List of request states to use as a filter. Multiple values mean union of the given filters.
            timeout: Timeout for the API HTTP request.
            cursor: A token returned in previous API response, to continue listing next page of requests
        """
        request_params = self._build_params(
            limit=limit,
            filter=','.join(filter) if filter else None,
            clientKey=self.client_key,
            cursor=cursor,
        )

        response = self._http_client.call(
            url=self._build_url('requests'),
            method='GET',
            params=request_params,
            timeout=timeout,
        )

        result = response_to_dict(response)
        return ListOfRequestsResponse.model_validate(result).data

    def iterate_requests(
        self,
        *,
        limit: int | None = None,
        filter: list[Literal['pending', 'locked']] | None = None,  # noqa: A002
        cursor: str | None = None,
        chunk_size: int | None = None,
        timeout: Timeout = 'medium',
    ) -> Iterator[RequestResource]:
        """Iterate over requests in the queue.

        Simple `list_requests` does only one API call, possibly not listing all items matching the criteria.
        This method returns an iterator that is capable of making multiple API calls to retrieve all items
        matching the criteria using the opaque `cursor` returned by the API.

        https://docs.apify.com/api/v2#/reference/request-queues/request-collection/list-requests

        Args:
            limit: Maximum number of requests to yield across all pages.
            filter: List of request states to use as a filter. Multiple values mean union of the given filters.
            cursor: A token returned in a previous API response, used as the initial pagination cursor.
            chunk_size: Maximum number of requests requested per API call when iterating across pages.
            timeout: Timeout for the API HTTP request.

        Yields:
            A request from the queue.
        """

        def _callback(*, cursor: str | None = None, limit: int | None = None) -> ListOfRequests:
            return self.list_requests(limit=limit, filter=filter, cursor=cursor, timeout=timeout)

        return get_cursor_iterator(
            _callback,
            cursor=cursor,
            limit=limit,
            chunk_size=chunk_size or DEFAULT_CHUNK_SIZE,
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

    async def get(self, *, timeout: Timeout = 'short') -> RequestQueueResource | None:
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
        title: str | None = None,
        general_access: GeneralAccess | None = None,
        timeout: Timeout = 'short',
    ) -> RequestQueueResource:
        """Update the request queue with specified fields.

        https://docs.apify.com/api/v2#/reference/request-queues/queue/update-request-queue

        Args:
            name: The new name for the request queue.
            title: The new title for the request queue.
            general_access: Determines how others can access the request queue.
            timeout: Timeout for the API HTTP request.

        Returns:
            The updated request queue.
        """
        result = await self._update(timeout=timeout, name=name, title=title, generalAccess=general_access)
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
        return RequestQueueHeadResponse.model_validate(result).data

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
        return LockedRequestQueueHeadResponse.model_validate(result).data

    async def add_request(
        self,
        request: RequestWithoutIdDict | RequestWithoutIdCamelDict | RequestWithoutId,
        *,
        forefront: bool | None = None,
        timeout: Timeout = 'short',
    ) -> RequestRegistration:
        """Add a request to the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/request-collection/add-request

        Args:
            request: The request to add to the queue. Must carry a `unique_key` and a `url`.
            forefront: Whether to add the request to the head or the end of the queue.
            timeout: Timeout for the API HTTP request.

        Returns:
            The added request.
        """
        if not isinstance(request, RequestWithoutId):
            request = RequestWithoutId.model_validate(request)

        request_params = self._build_params(forefront=forefront, clientKey=self.client_key)

        response = await self._http_client.call(
            url=self._build_url('requests'),
            method='POST',
            json=request.model_dump(mode='json', by_alias=True, exclude_none=True, fallback=str),
            params=request_params,
            timeout=timeout,
        )

        result = response_to_dict(response)
        return AddRequestResponse.model_validate(result).data

    async def get_request(self, request_id: str, *, timeout: Timeout = 'short') -> RequestResource | None:
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
                url=self._build_url(f'requests/{to_path_segment(request_id)}'),
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
        request: RequestResourceDict | RequestResourceCamelDict | RequestResource,
        *,
        forefront: bool | None = None,
        timeout: Timeout = 'medium',
    ) -> RequestRegistration:
        """Update a request in the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/request/update-request

        Args:
            request: The updated request. It must carry the ID of the request to update.
            forefront: Whether to put the updated request in the beginning or the end of the queue.
            timeout: Timeout for the API HTTP request.

        Returns:
            The updated request.

        Raises:
            ValueError: If the request carries no ID.
        """
        if not isinstance(request, RequestResource):
            request = RequestResource.model_validate(request)

        if request.id is None:
            raise ValueError('The request to update must have an ID.')

        request_params = self._build_params(forefront=forefront, clientKey=self.client_key)

        response = await self._http_client.call(
            url=self._build_url(f'requests/{to_path_segment(request.id)}'),
            method='PUT',
            json=request.model_dump(mode='json', by_alias=True, exclude_none=True, fallback=str),
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
            url=self._build_url(f'requests/{to_path_segment(request_id)}'),
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
            url=self._build_url(f'requests/{to_path_segment(request_id)}/lock'),
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
            url=self._build_url(f'requests/{to_path_segment(request_id)}/lock'),
            method='DELETE',
            params=request_params,
            timeout=timeout,
        )

    async def _batch_add_requests_worker(
        self,
        *,
        queue: asyncio.Queue[Iterable[tuple[str, bytes]]],
        request_params: QueryParams,
        max_unprocessed_requests_retries: int,
        min_delay_between_unprocessed_requests_retries: timedelta,
        timeout: Timeout,
    ) -> BatchAddResponse:
        """Worker function to process a batch of requests.

        This worker will process batches from the queue, retrying any unprocessed requests with exponential backoff.

        Return result containing lists of processed and unprocessed requests by the worker.
        """
        processed_requests = list[AddedRequest]()
        unprocessed_requests = list[UnprocessedRequest]()

        while True:
            # Get the next batch from the queue.
            try:
                request_batch = await queue.get()
            except asyncio.CancelledError:
                break

            try:
                batch_items = list(request_batch)
                remaining_items = batch_items
                processed_unique_keys = frozenset[str]()
                batch_processed_requests = list[AddedRequest]()
                batch_unprocessed_requests = list[UnprocessedRequest]()

                for attempt in range(1 + max_unprocessed_requests_retries):
                    try:
                        response = await self._http_client.call(
                            url=self._build_url('requests/batch'),
                            method='POST',
                            headers={'content-type': 'application/json'},
                            params=request_params,
                            data=b'[' + b','.join(payload for _, payload in remaining_items) + b']',
                            timeout=timeout,
                        )
                        result = response_to_dict(response)
                        batch_response = BatchAddResponse.model_validate(result)
                    except Exception:
                        if attempt == 0:
                            raise
                        logger.exception(
                            'Failed to retry unprocessed requests in request queue batch; returning partial result.'
                        )
                        break

                    attempt_result = _extract_batch_attempt_result(
                        batch_items=batch_items,
                        batch_response=batch_response,
                        already_processed_keys=processed_unique_keys,
                    )
                    batch_processed_requests.extend(attempt_result.processed_requests)
                    batch_unprocessed_requests = attempt_result.unprocessed_requests
                    remaining_items = attempt_result.remaining_items
                    processed_unique_keys = attempt_result.processed_unique_keys
                    if batch_unprocessed_requests:
                        self._http_client.stats.add_rate_limit_error(attempt + 1)
                    if not remaining_items:
                        break

                    if attempt < max_unprocessed_requests_retries:
                        await asyncio.sleep(
                            _compute_retry_delay_seconds(attempt, min_delay_between_unprocessed_requests_retries)
                        )

                processed_requests.extend(batch_processed_requests)
                unprocessed_requests.extend(batch_unprocessed_requests)

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
        requests: list[RequestWithoutId] | list[RequestWithoutIdDict] | list[RequestWithoutIdCamelDict],
        *,
        forefront: bool = False,
        max_parallel: int = 5,
        max_unprocessed_requests_retries: int = DEFAULT_UNPROCESSED_RETRIES_BATCH_ADD_REQUESTS,
        min_delay_between_unprocessed_requests_retries: timedelta = (
            DEFAULT_MIN_DELAY_BETWEEN_UNPROCESSED_REQUESTS_RETRIES
        ),
        timeout: Timeout = 'medium',
    ) -> BatchAddResult:
        """Add requests to the request queue in batches.

        Requests are split into batches based on size and processed in parallel. Any requests reported as unprocessed
        by the API are retried with exponential backoff.

        https://docs.apify.com/api/v2#/reference/request-queues/batch-request-operations/add-requests

        Args:
            requests: List of requests to be added to the queue. Each must carry a `unique_key` and a `url`.
            forefront: Whether to add requests to the front of the queue.
            max_parallel: Specifies the maximum number of parallel tasks for API calls. This is only applicable
                to the async client. For the sync client, this value must be set to 1, as parallel execution
                is not supported.
            max_unprocessed_requests_retries: Maximum number of retry attempts for requests returned as unprocessed
                by the API.
            min_delay_between_unprocessed_requests_retries: Minimum delay before retrying unprocessed requests.
            timeout: Timeout for the API HTTP request.

        Returns:
            Result containing lists of processed and unprocessed requests.
        """
        _validate_batch_retry_params(
            max_unprocessed_requests_retries=max_unprocessed_requests_retries,
            min_delay_between_unprocessed_requests_retries=min_delay_between_unprocessed_requests_retries,
        )

        # Validate and serialize the requests in a worker thread, as it is CPU-bound and would block the event loop.
        serialized_requests = await asyncio.to_thread(_serialize_requests, requests)

        # Build the query parameters shared by all the batch API calls.
        request_params = self._build_params(clientKey=self.client_key, forefront=forefront)

        # Compute the payload size limit to ensure it doesn't exceed the maximum allowed size.
        payload_size_limit_bytes = _MAX_PAYLOAD_SIZE_BYTES - math.ceil(_MAX_PAYLOAD_SIZE_BYTES * _SAFETY_BUFFER_PERCENT)

        # Split the requests into batches by payload size (counting commas and brackets) and max requests per batch.
        batches = constrained_batches(
            serialized_requests,
            max_size=payload_size_limit_bytes - len(b'[]'),
            max_count=_RQ_MAX_REQUESTS_PER_BATCH,
            get_len=lambda item: len(item[1]) + len(b','),
            strict=False,
        )

        # Create a queue with all the batches, from which the worker tasks will consume them.
        batch_queue: asyncio.Queue[Iterable[tuple[str, bytes]]] = asyncio.Queue()

        for batch in batches:
            await batch_queue.put(batch)

        # Use TaskGroup for structured concurrency — automatic cleanup and error propagation.
        try:
            async with asyncio.TaskGroup() as tg:
                workers = [
                    tg.create_task(
                        self._batch_add_requests_worker(
                            queue=batch_queue,
                            request_params=request_params,
                            max_unprocessed_requests_retries=max_unprocessed_requests_retries,
                            min_delay_between_unprocessed_requests_retries=(
                                min_delay_between_unprocessed_requests_retries
                            ),
                            timeout=timeout,
                        ),
                        name=f'batch_add_requests_worker_{i}',
                    )
                    for i in range(max_parallel)
                ]

                # Wait for all batches to be processed, then cancel idle workers.
                await batch_queue.join()
                for worker in workers:
                    worker.cancel()
        except ExceptionGroup as eg:
            # Re-raise the first worker exception directly to maintain backward-compatible error types.
            raise eg.exceptions[0] from None

        # Combine the results from all workers and return them.
        processed_requests = list[AddedRequest]()
        unprocessed_requests = list[UnprocessedRequest]()

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
        requests: list[RequestToDelete] | list[RequestToDeleteDict] | list[RequestToDeleteCamelDict],
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
            (
                request
                if isinstance(request, RequestToDelete)
                else RequestToDelete.model_validate(
                    request,
                )
            ).root.model_dump(mode='json', by_alias=True, exclude_none=True, fallback=str)
            for request in requests
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

    async def list_requests(
        self,
        *,
        limit: int | None = None,
        filter: list[Literal['pending', 'locked']] | None = None,  # noqa: A002
        timeout: Timeout = 'medium',
        cursor: str | None = None,
    ) -> ListOfRequests:
        """List requests in the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/request-collection/list-requests

        Args:
            limit: How many requests to retrieve.
            filter: List of request states to use as a filter. Multiple values mean union of the given filters.
            timeout: Timeout for the API HTTP request.
            cursor: A token returned in previous API response, to continue listing next page of requests
        """
        request_params = self._build_params(
            limit=limit,
            filter=','.join(filter) if filter else None,
            clientKey=self.client_key,
            cursor=cursor,
        )

        response = await self._http_client.call(
            url=self._build_url('requests'),
            method='GET',
            params=request_params,
            timeout=timeout,
        )

        result = response_to_dict(response)
        return ListOfRequestsResponse.model_validate(result).data

    def iterate_requests(
        self,
        *,
        limit: int | None = None,
        filter: list[Literal['pending', 'locked']] | None = None,  # noqa: A002
        cursor: str | None = None,
        chunk_size: int | None = None,
        timeout: Timeout = 'medium',
    ) -> AsyncIterator[RequestResource]:
        """Iterate over requests in the queue.

        Simple `list_requests` does only one API call, possibly not listing all items matching the criteria.
        This method returns an iterator that is capable of making multiple API calls to retrieve all items
        matching the criteria using the opaque `cursor` returned by the API.

        https://docs.apify.com/api/v2#/reference/request-queues/request-collection/list-requests

        Args:
            limit: Maximum number of requests to yield across all pages.
            filter: List of request states to use as a filter. Multiple values mean union of the given filters.
            cursor: A token returned in a previous API response, used as the initial pagination cursor.
            chunk_size: Maximum number of requests requested per API call when iterating across pages.
            timeout: Timeout for the API HTTP request.

        Yields:
            A request from the queue.
        """

        async def _callback(*, cursor: str | None = None, limit: int | None = None) -> ListOfRequests:
            return await self.list_requests(limit=limit, filter=filter, cursor=cursor, timeout=timeout)

        return get_cursor_iterator_async(
            _callback,
            cursor=cursor,
            limit=limit,
            chunk_size=chunk_size or DEFAULT_CHUNK_SIZE,
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
