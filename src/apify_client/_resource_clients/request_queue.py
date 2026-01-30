from __future__ import annotations

import asyncio
import logging
import math
from collections.abc import Iterable
from datetime import timedelta
from queue import Queue
from typing import TYPE_CHECKING, Any

from more_itertools import constrained_batches

from apify_client._consts import FAST_OPERATION_TIMEOUT, STANDARD_OPERATION_TIMEOUT
from apify_client._models import (
    AddedRequest,
    AddRequestResponse,
    BatchAddResponse,
    BatchAddResult,
    BatchDeleteResponse,
    BatchDeleteResult,
    GetHeadAndLockResponse,
    GetHeadResponse,
    GetListOfRequestsResponse,
    GetRequestQueueResponse,
    GetRequestResponse,
    ListOfRequests,
    LockedRequestQueueHead,
    ProlongRequestLockResponse,
    Request,
    RequestDraft,
    RequestLockInfo,
    RequestQueue,
    RequestQueueHead,
    RequestRegistration,
    UnlockRequestsResponse,
    UnlockRequestsResult,
)
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync
from apify_client._utils import catch_not_found_or_throw, filter_none_values, response_to_dict, to_seconds
from apify_client.errors import ApifyApiError

if TYPE_CHECKING:
    from datetime import timedelta

    from apify_client._consts import StorageGeneralAccess


logger = logging.getLogger(__name__)

_RQ_MAX_REQUESTS_PER_BATCH = 25
_MAX_PAYLOAD_SIZE_BYTES = 9 * 1024 * 1024  # 9 MB
_SAFETY_BUFFER_PERCENT = 0.01 / 100  # 0.01%


class RequestQueueClient(ResourceClient):
    """Sub-client for manipulating a single request queue."""

    def __init__(  # noqa: D417
        self,
        *args: Any,
        client_key: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize a new instance.

        Args:
            client_key: A unique identifier of the client accessing the request queue.
        """
        resource_path = kwargs.pop('resource_path', 'request-queues')
        super().__init__(*args, resource_path=resource_path, **kwargs)
        self.client_key = client_key

    def get(self) -> RequestQueue | None:
        """Retrieve the request queue.

        https://docs.apify.com/api/v2#/reference/request-queues/queue/get-request-queue

        Returns:
            The retrieved request queue, or None, if it does not exist.
        """
        try:
            response = self._http_client.call(
                url=self._build_url(),
                method='GET',
                params=self._build_params(),
                timeout=FAST_OPERATION_TIMEOUT,
            )
            result = response_to_dict(response)
            return GetRequestQueueResponse.model_validate(result).data
        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)
            return None

    def update(self, *, name: str | None = None, general_access: StorageGeneralAccess | None = None) -> RequestQueue:
        """Update the request queue with specified fields.

        https://docs.apify.com/api/v2#/reference/request-queues/queue/update-request-queue

        Args:
            name: The new name for the request queue.
            general_access: Determines how others can access the request queue.

        Returns:
            The updated request queue.
        """
        updated_fields = {
            'name': name,
            'generalAccess': general_access,
        }
        cleaned = filter_none_values(updated_fields)

        response = self._http_client.call(
            url=self._build_url(),
            method='PUT',
            params=self._build_params(),
            json=cleaned,
            timeout=FAST_OPERATION_TIMEOUT,
        )
        result = response_to_dict(response)
        return GetRequestQueueResponse.model_validate(result).data

    def delete(self) -> None:
        """Delete the request queue.

        https://docs.apify.com/api/v2#/reference/request-queues/queue/delete-request-queue
        """
        try:
            self._http_client.call(
                url=self._build_url(),
                method='DELETE',
                params=self._build_params(),
                timeout=FAST_OPERATION_TIMEOUT,
            )
        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

    def list_head(self, *, limit: int | None = None) -> RequestQueueHead:
        """Retrieve a given number of requests from the beginning of the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/queue-head/get-head

        Args:
            limit: How many requests to retrieve.

        Returns:
            The desired number of requests from the beginning of the queue.
        """
        request_params = self._build_params(limit=limit, clientKey=self.client_key)

        response = self._http_client.call(
            url=self._build_url('head'),
            method='GET',
            params=request_params,
            timeout=FAST_OPERATION_TIMEOUT,
        )

        result = response.json()
        return GetHeadResponse.model_validate(result).data

    def list_and_lock_head(self, *, lock_duration: timedelta, limit: int | None = None) -> LockedRequestQueueHead:
        """Retrieve a given number of unlocked requests from the beginning of the queue and lock them for a given time.

        https://docs.apify.com/api/v2#/reference/request-queues/queue-head-with-locks/get-head-and-lock

        Args:
            lock_duration: How long the requests will be locked for.
            limit: How many requests to retrieve.

        Returns:
            The desired number of locked requests from the beginning of the queue.
        """
        request_params = self._build_params(lockSecs=to_seconds(lock_duration), limit=limit, clientKey=self.client_key)

        response = self._http_client.call(
            url=self._build_url('head/lock'),
            method='POST',
            params=request_params,
            timeout=STANDARD_OPERATION_TIMEOUT,
        )

        result = response.json()
        return GetHeadAndLockResponse.model_validate(result).data

    def add_request(self, request: dict, *, forefront: bool | None = None) -> RequestRegistration:
        """Add a request to the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/request-collection/add-request

        Args:
            request: The request to add to the queue.
            forefront: Whether to add the request to the head or the end of the queue.

        Returns:
            The added request.
        """
        request_params = self._build_params(forefront=forefront, clientKey=self.client_key)

        response = self._http_client.call(
            url=self._build_url('requests'),
            method='POST',
            json=request,
            params=request_params,
            timeout=FAST_OPERATION_TIMEOUT,
        )

        result = response.json()
        return AddRequestResponse.model_validate(result).data

    def get_request(self, request_id: str) -> Request | None:
        """Retrieve a request from the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/request/get-request

        Args:
            request_id: ID of the request to retrieve.

        Returns:
            The retrieved request, or None, if it did not exist.
        """
        try:
            response = self._http_client.call(
                url=self._build_url(f'requests/{request_id}'),
                method='GET',
                params=self._build_params(),
                timeout=FAST_OPERATION_TIMEOUT,
            )
            result = response.json()
            return GetRequestResponse.model_validate(result).data

        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

        return None

    def update_request(self, request: dict, *, forefront: bool | None = None) -> RequestRegistration:
        """Update a request in the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/request/update-request

        Args:
            request: The updated request.
            forefront: Whether to put the updated request in the beginning or the end of the queue.

        Returns:
            The updated request.
        """
        request_id = request['id']

        request_params = self._build_params(forefront=forefront, clientKey=self.client_key)

        response = self._http_client.call(
            url=self._build_url(f'requests/{request_id}'),
            method='PUT',
            json=request,
            params=request_params,
            timeout=STANDARD_OPERATION_TIMEOUT,
        )

        result = response.json()
        return AddRequestResponse.model_validate(result).data

    def delete_request(self, request_id: str) -> None:
        """Delete a request from the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/request/delete-request

        Args:
            request_id: ID of the request to delete.
        """
        request_params = self._build_params(
            clientKey=self.client_key,
        )

        self._http_client.call(
            url=self._build_url(f'requests/{request_id}'),
            method='DELETE',
            params=request_params,
            timeout=FAST_OPERATION_TIMEOUT,
        )

    def prolong_request_lock(
        self,
        request_id: str,
        *,
        forefront: bool | None = None,
        lock_duration: timedelta,
    ) -> RequestLockInfo | None:
        """Prolong the lock on a request.

        https://docs.apify.com/api/v2#/reference/request-queues/request-lock/prolong-request-lock

        Args:
            request_id: ID of the request to prolong the lock.
            forefront: Whether to put the request in the beginning or the end of the queue after lock expires.
            lock_duration: By how much to prolong the lock.
        """
        request_params = self._build_params(
            clientKey=self.client_key, forefront=forefront, lockSecs=to_seconds(lock_duration)
        )

        response = self._http_client.call(
            url=self._build_url(f'requests/{request_id}/lock'),
            method='PUT',
            params=request_params,
            timeout=STANDARD_OPERATION_TIMEOUT,
        )

        result = response.json()
        return ProlongRequestLockResponse.model_validate(result).data

    def delete_request_lock(self, request_id: str, *, forefront: bool | None = None) -> None:
        """Delete the lock on a request.

        https://docs.apify.com/api/v2#/reference/request-queues/request-lock/delete-request-lock

        Args:
            request_id: ID of the request to delete the lock.
            forefront: Whether to put the request in the beginning or the end of the queue after the lock is deleted.
        """
        request_params = self._build_params(clientKey=self.client_key, forefront=forefront)

        self._http_client.call(
            url=self._build_url(f'requests/{request_id}/lock'),
            method='DELETE',
            params=request_params,
            timeout=FAST_OPERATION_TIMEOUT,
        )

    def batch_add_requests(
        self,
        requests: list[dict],
        *,
        forefront: bool = False,
        max_parallel: int = 1,
        max_unprocessed_requests_retries: int | None = None,
        min_delay_between_unprocessed_requests_retries: timedelta | None = None,
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

        Returns:
            Result containing lists of processed and unprocessed requests.
        """
        if max_unprocessed_requests_retries:
            logger.warning('`max_unprocessed_requests_retries` is deprecated and not used anymore.')
        if min_delay_between_unprocessed_requests_retries:
            logger.warning('`min_delay_between_unprocessed_requests_retries` is deprecated and not used anymore.')

        if max_parallel != 1:
            raise NotImplementedError('max_parallel is only supported in async client')

        request_params = self._build_params(clientKey=self.client_key, forefront=forefront)

        # Compute the payload size limit to ensure it doesn't exceed the maximum allowed size.
        payload_size_limit_bytes = _MAX_PAYLOAD_SIZE_BYTES - math.ceil(_MAX_PAYLOAD_SIZE_BYTES * _SAFETY_BUFFER_PERCENT)

        # Split the requests into batches, constrained by the max payload size and max requests per batch.
        batches = constrained_batches(
            requests,
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
                timeout=STANDARD_OPERATION_TIMEOUT,
            )

            response_parsed = response.json()
            batch_response = BatchAddResponse.model_validate(response_parsed)
            processed_requests.extend(batch_response.data.processed_requests)
            unprocessed_requests.extend(batch_response.data.unprocessed_requests)

        return BatchAddResponse.model_construct(
            data=BatchAddResult.model_construct(
                processed_requests=processed_requests,
                unprocessed_requests=unprocessed_requests,
            )
        ).data

    def batch_delete_requests(self, requests: list[dict]) -> BatchDeleteResult:
        """Delete given requests from the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/batch-request-operations/delete-requests

        Args:
            requests: List of the requests to delete.
        """
        request_params = self._build_params(clientKey=self.client_key)

        response = self._http_client.call(
            url=self._build_url('requests/batch'),
            method='DELETE',
            params=request_params,
            json=requests,
            timeout=FAST_OPERATION_TIMEOUT,
        )

        result = response.json()
        return BatchDeleteResponse.model_validate(result).data

    def list_requests(
        self,
        *,
        limit: int | None = None,
        exclusive_start_id: str | None = None,
    ) -> ListOfRequests:
        """List requests in the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/request-collection/list-requests

        Args:
            limit: How many requests to retrieve.
            exclusive_start_id: All requests up to this one (including) are skipped from the result.
        """
        request_params = self._build_params(limit=limit, exclusiveStartId=exclusive_start_id, clientKey=self.client_key)

        response = self._http_client.call(
            url=self._build_url('requests'),
            method='GET',
            params=request_params,
            timeout=STANDARD_OPERATION_TIMEOUT,
        )

        result = response.json()
        return GetListOfRequestsResponse.model_validate(result).data

    def unlock_requests(self: RequestQueueClient) -> UnlockRequestsResult:
        """Unlock all requests in the queue, which were locked by the same clientKey or from the same Actor run.

        https://docs.apify.com/api/v2#/reference/request-queues/request-collection/unlock-requests

        Returns:
            Result of the unlock operation containing the count of unlocked requests
        """
        request_params = self._build_params(clientKey=self.client_key)

        response = self._http_client.call(
            url=self._build_url('requests/unlock'),
            method='POST',
            params=request_params,
        )

        result = response.json()
        return UnlockRequestsResponse.model_validate(result).data


class RequestQueueClientAsync(ResourceClientAsync):
    """Async sub-client for manipulating a single request queue."""

    def __init__(  # noqa: D417
        self,
        *args: Any,
        client_key: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize a new instance.

        Args:
            client_key: A unique identifier of the client accessing the request queue.
        """
        resource_path = kwargs.pop('resource_path', 'request-queues')
        super().__init__(*args, resource_path=resource_path, **kwargs)
        self.client_key = client_key

    async def get(self) -> RequestQueue | None:
        """Retrieve the request queue.

        https://docs.apify.com/api/v2#/reference/request-queues/queue/get-request-queue

        Returns:
            The retrieved request queue, or None, if it does not exist.
        """
        try:
            response = await self._http_client.call(
                url=self._build_url(),
                method='GET',
                params=self._build_params(),
                timeout=FAST_OPERATION_TIMEOUT,
            )
            result = response_to_dict(response)
            return GetRequestQueueResponse.model_validate(result).data
        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)
            return None

    async def update(
        self,
        *,
        name: str | None = None,
        general_access: StorageGeneralAccess | None = None,
    ) -> RequestQueue:
        """Update the request queue with specified fields.

        https://docs.apify.com/api/v2#/reference/request-queues/queue/update-request-queue

        Args:
            name: The new name for the request queue.
            general_access: Determines how others can access the request queue.

        Returns:
            The updated request queue.
        """
        updated_fields = {
            'name': name,
            'generalAccess': general_access,
        }
        cleaned = filter_none_values(updated_fields)

        response = await self._http_client.call(
            url=self._build_url(),
            method='PUT',
            params=self._build_params(),
            json=cleaned,
            timeout=FAST_OPERATION_TIMEOUT,
        )
        result = response_to_dict(response)
        return GetRequestQueueResponse.model_validate(result).data

    async def delete(self) -> None:
        """Delete the request queue.

        https://docs.apify.com/api/v2#/reference/request-queues/queue/delete-request-queue
        """
        try:
            await self._http_client.call(
                url=self._build_url(),
                method='DELETE',
                params=self._build_params(),
                timeout=FAST_OPERATION_TIMEOUT,
            )
        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

    async def list_head(self, *, limit: int | None = None) -> RequestQueueHead:
        """Retrieve a given number of requests from the beginning of the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/queue-head/get-head

        Args:
            limit: How many requests to retrieve.

        Returns:
            The desired number of requests from the beginning of the queue.
        """
        request_params = self._build_params(limit=limit, clientKey=self.client_key)

        response = await self._http_client.call(
            url=self._build_url('head'),
            method='GET',
            params=request_params,
            timeout=FAST_OPERATION_TIMEOUT,
        )

        result = response.json()
        return GetHeadResponse.model_validate(result).data

    async def list_and_lock_head(self, *, lock_duration: timedelta, limit: int | None = None) -> LockedRequestQueueHead:
        """Retrieve a given number of unlocked requests from the beginning of the queue and lock them for a given time.

        https://docs.apify.com/api/v2#/reference/request-queues/queue-head-with-locks/get-head-and-lock

        Args:
            lock_duration: How long the requests will be locked for.
            limit: How many requests to retrieve.

        Returns:
            The desired number of locked requests from the beginning of the queue.
        """
        request_params = self._build_params(lockSecs=to_seconds(lock_duration), limit=limit, clientKey=self.client_key)

        response = await self._http_client.call(
            url=self._build_url('head/lock'),
            method='POST',
            params=request_params,
            timeout=STANDARD_OPERATION_TIMEOUT,
        )

        result = response.json()
        return GetHeadAndLockResponse.model_validate(result).data

    async def add_request(self, request: dict, *, forefront: bool | None = None) -> RequestRegistration:
        """Add a request to the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/request-collection/add-request

        Args:
            request: The request to add to the queue.
            forefront: Whether to add the request to the head or the end of the queue.

        Returns:
            The added request.
        """
        request_params = self._build_params(forefront=forefront, clientKey=self.client_key)

        response = await self._http_client.call(
            url=self._build_url('requests'),
            method='POST',
            json=request,
            params=request_params,
            timeout=FAST_OPERATION_TIMEOUT,
        )

        result = response.json()
        return AddRequestResponse.model_validate(result).data

    async def get_request(self, request_id: str) -> Request | None:
        """Retrieve a request from the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/request/get-request

        Args:
            request_id: ID of the request to retrieve.

        Returns:
            The retrieved request, or None, if it did not exist.
        """
        try:
            response = await self._http_client.call(
                url=self._build_url(f'requests/{request_id}'),
                method='GET',
                params=self._build_params(),
                timeout=FAST_OPERATION_TIMEOUT,
            )
            result = response.json()
            validated_response = GetRequestResponse.model_validate(result) if result is not None else None
        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)
            return None
        else:
            return validated_response.data if validated_response is not None else None

    async def update_request(self, request: dict, *, forefront: bool | None = None) -> RequestRegistration:
        """Update a request in the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/request/update-request

        Args:
            request: The updated request.
            forefront: Whether to put the updated request in the beginning or the end of the queue.

        Returns:
            The updated request.
        """
        request_id = request['id']

        request_params = self._build_params(forefront=forefront, clientKey=self.client_key)

        response = await self._http_client.call(
            url=self._build_url(f'requests/{request_id}'),
            method='PUT',
            json=request,
            params=request_params,
            timeout=STANDARD_OPERATION_TIMEOUT,
        )

        result = response.json()
        return AddRequestResponse.model_validate(result).data

    async def delete_request(self, request_id: str) -> None:
        """Delete a request from the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/request/delete-request

        Args:
            request_id: ID of the request to delete.
        """
        request_params = self._build_params(clientKey=self.client_key)

        await self._http_client.call(
            url=self._build_url(f'requests/{request_id}'),
            method='DELETE',
            params=request_params,
            timeout=FAST_OPERATION_TIMEOUT,
        )

    async def prolong_request_lock(
        self,
        request_id: str,
        *,
        forefront: bool | None = None,
        lock_duration: timedelta,
    ) -> RequestLockInfo | None:
        """Prolong the lock on a request.

        https://docs.apify.com/api/v2#/reference/request-queues/request-lock/prolong-request-lock

        Args:
            request_id: ID of the request to prolong the lock.
            forefront: Whether to put the request in the beginning or the end of the queue after lock expires.
            lock_duration: By how much to prolong the lock.
        """
        request_params = self._build_params(
            clientKey=self.client_key, forefront=forefront, lockSecs=to_seconds(lock_duration)
        )

        response = await self._http_client.call(
            url=self._build_url(f'requests/{request_id}/lock'),
            method='PUT',
            params=request_params,
            timeout=STANDARD_OPERATION_TIMEOUT,
        )

        result = response.json()
        return ProlongRequestLockResponse.model_validate(result).data

    async def delete_request_lock(
        self,
        request_id: str,
        *,
        forefront: bool | None = None,
    ) -> None:
        """Delete the lock on a request.

        https://docs.apify.com/api/v2#/reference/request-queues/request-lock/delete-request-lock

        Args:
            request_id: ID of the request to delete the lock.
            forefront: Whether to put the request in the beginning or the end of the queue after the lock is deleted.
        """
        request_params = self._build_params(clientKey=self.client_key, forefront=forefront)

        await self._http_client.call(
            url=self._build_url(f'requests/{request_id}/lock'),
            method='DELETE',
            params=request_params,
            timeout=FAST_OPERATION_TIMEOUT,
        )

    async def _batch_add_requests_worker(
        self,
        queue: asyncio.Queue[Iterable[dict]],
        request_params: dict,
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
                    timeout=STANDARD_OPERATION_TIMEOUT,
                )

                response_parsed = response.json()
                batch_response = BatchAddResponse.model_validate(response_parsed)
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
        requests: list[dict],
        *,
        forefront: bool = False,
        max_parallel: int = 5,
        max_unprocessed_requests_retries: int | None = None,
        min_delay_between_unprocessed_requests_retries: timedelta | None = None,
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

        Returns:
            Result containing lists of processed and unprocessed requests.
        """
        if max_unprocessed_requests_retries:
            logger.warning('`max_unprocessed_requests_retries` is deprecated and not used anymore.')
        if min_delay_between_unprocessed_requests_retries:
            logger.warning('`min_delay_between_unprocessed_requests_retries` is deprecated and not used anymore.')

        tasks = set[asyncio.Task]()
        asyncio_queue: asyncio.Queue[Iterable[dict]] = asyncio.Queue()
        request_params = self._build_params(clientKey=self.client_key, forefront=forefront)

        # Compute the payload size limit to ensure it doesn't exceed the maximum allowed size.
        payload_size_limit_bytes = _MAX_PAYLOAD_SIZE_BYTES - math.ceil(_MAX_PAYLOAD_SIZE_BYTES * _SAFETY_BUFFER_PERCENT)

        # Split the requests into batches, constrained by the max payload size and max requests per batch.
        batches = constrained_batches(
            requests,
            max_size=payload_size_limit_bytes,
            max_count=_RQ_MAX_REQUESTS_PER_BATCH,
        )

        for batch in batches:
            await asyncio_queue.put(batch)

        # Start a required number of worker tasks to process the batches.
        for i in range(max_parallel):
            coro = self._batch_add_requests_worker(
                asyncio_queue,
                request_params,
            )
            task = asyncio.create_task(coro, name=f'batch_add_requests_worker_{i}')
            tasks.add(task)

        # Wait for all batches to be processed.
        await asyncio_queue.join()

        # Send cancellation signals to all worker tasks and wait for them to finish.
        for task in tasks:
            task.cancel()

        results: list[BatchAddResponse] = await asyncio.gather(*tasks)

        # Combine the results from all workers and return them.
        processed_requests = list[AddedRequest]()
        unprocessed_requests = list[RequestDraft]()

        for result in results:
            processed_requests.extend(result.data.processed_requests)
            unprocessed_requests.extend(result.data.unprocessed_requests)

        return BatchAddResponse.model_construct(
            data=BatchAddResult.model_construct(
                processed_requests=processed_requests,
                unprocessed_requests=unprocessed_requests,
            )
        ).data

    async def batch_delete_requests(self, requests: list[dict]) -> BatchDeleteResult:
        """Delete given requests from the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/batch-request-operations/delete-requests

        Args:
            requests: List of the requests to delete.
        """
        request_params = self._build_params(clientKey=self.client_key)

        response = await self._http_client.call(
            url=self._build_url('requests/batch'),
            method='DELETE',
            params=request_params,
            json=requests,
            timeout=FAST_OPERATION_TIMEOUT,
        )
        result = response.json()
        return BatchDeleteResponse.model_validate(result).data

    async def list_requests(
        self,
        *,
        limit: int | None = None,
        exclusive_start_id: str | None = None,
    ) -> ListOfRequests:
        """List requests in the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/request-collection/list-requests

        Args:
            limit: How many requests to retrieve.
            exclusive_start_id: All requests up to this one (including) are skipped from the result.
        """
        request_params = self._build_params(limit=limit, exclusiveStartId=exclusive_start_id, clientKey=self.client_key)

        response = await self._http_client.call(
            url=self._build_url('requests'),
            method='GET',
            params=request_params,
            timeout=STANDARD_OPERATION_TIMEOUT,
        )

        result = response.json()
        return GetListOfRequestsResponse.model_validate(result).data

    async def unlock_requests(self: RequestQueueClientAsync) -> UnlockRequestsResult:
        """Unlock all requests in the queue, which were locked by the same clientKey or from the same Actor run.

        https://docs.apify.com/api/v2#/reference/request-queues/request-collection/unlock-requests

        Returns:
            Result of the unlock operation containing the count of unlocked requests
        """
        request_params = self._build_params(clientKey=self.client_key)

        response = await self._http_client.call(
            url=self._build_url('requests/unlock'),
            method='POST',
            params=request_params,
        )

        result = response.json()
        return UnlockRequestsResponse.model_validate(result).data
