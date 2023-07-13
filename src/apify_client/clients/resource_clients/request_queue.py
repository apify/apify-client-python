import asyncio
import random
from time import sleep
from typing import Any, Dict, List, Optional

from ..._errors import ApifyApiError
from ..._utils import _catch_not_found_or_throw, _filter_out_none_values_recursively, _parse_date_fields, _pluck_data, ignore_docs
from ..base import ResourceClient, ResourceClientAsync

MAX_REQUESTS_PER_BATCH_OPERATION = 25
DEFAULT_PARALLEL_BATCH_ADD_REQUESTS = 5
DEFAULT_UNPROCESSED_RETRIES_BATCH_ADD_REQUESTS = 3
DEFAULT_MIN_DELAY_BETWEEN_UNPROCESSED_REQUESTS_RETRIES_MILLIS = 500
DEFAULT_REQUEST_QUEUE_REQUEST_PAGE_LIMIT = 1000


class RequestQueueClient(ResourceClient):
    """Sub-client for manipulating a single request queue."""

    @ignore_docs
    def __init__(self, *args: Any, client_key: Optional[str] = None, **kwargs: Any) -> None:
        """Initialize the RequestQueueClient.

        Args:
            client_key (str, optional): A unique identifier of the client accessing the request queue
        """
        resource_path = kwargs.pop('resource_path', 'request-queues')
        super().__init__(*args, resource_path=resource_path, **kwargs)
        self.client_key = client_key

    def get(self) -> Optional[Dict]:
        """Retrieve the request queue.

        https://docs.apify.com/api/v2#/reference/request-queues/queue/get-request-queue

        Returns:
            dict, optional: The retrieved request queue, or None, if it does not exist
        """
        return self._get()

    def update(self, *, name: Optional[str] = None) -> Dict:
        """Update the request queue with specified fields.

        https://docs.apify.com/api/v2#/reference/request-queues/queue/update-request-queue

        Args:
            name (str, optional): The new name for the request queue

        Returns:
            dict: The updated request queue
        """
        updated_fields = {
            'name': name,
        }

        return self._update(_filter_out_none_values_recursively(updated_fields))

    def delete(self) -> None:
        """Delete the request queue.

        https://docs.apify.com/api/v2#/reference/request-queues/queue/delete-request-queue
        """
        return self._delete()

    def list_head(self, *, limit: Optional[int] = None) -> Dict:
        """Retrieve a given number of requests from the beginning of the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/queue-head/get-head

        Args:
            limit (int, optional): How many requests to retrieve

        Returns:
            dict: The desired number of requests from the beginning of the queue.
        """
        request_params = self._params(limit=limit, clientKey=self.client_key)

        response = self.http_client.call(
            url=self._url('head'),
            method='GET',
            params=request_params,
        )

        return _parse_date_fields(_pluck_data(response.json()))

    def list_and_lock_head(self, *, lock_secs: int, limit: Optional[int] = None) -> Dict:
        """Retrieve the given number of first requests from the queue and locks them for the given time.

        https://docs.apify.com/api/v2#/reference/request-queues/queue-head-with-locks/get-head-and-lock

        Args:
            lock_secs (int): How long the second request will be locked for
            limit (int, optional): How many requests to retrieve


        Returns:
            dict: The desired number of locked requests from the beginning of the queue.
        """
        request_params = self._params(lockSecs=lock_secs, limit=limit, clientKey=self.client_key)

        response = self.http_client.call(
            url=self._url('head/lock'),
            method='POST',
            params=request_params,
        )

        return _parse_date_fields(_pluck_data(response.json()))

    def add_request(self, request: Dict, *, forefront: Optional[bool] = None) -> Dict:
        """Add a request to the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/request-collection/add-request

        Args:
            request (dict): The request to add to the queue
            forefront (bool, optional): Whether to add the request to the head or the end of the queue

        Returns:
            dict: The added request.
        """
        request_params = self._params(
            forefront=forefront,
            clientKey=self.client_key,
        )

        response = self.http_client.call(
            url=self._url('requests'),
            method='POST',
            json=request,
            params=request_params,
        )

        return _parse_date_fields(_pluck_data(response.json()))

    def get_request(self, request_id: str) -> Optional[Dict]:
        """Retrieve a request from the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/request/get-request

        Args:
            request_id (str): ID of the request to retrieve

        Returns:
            dict, optional: The retrieved request, or None, if it did not exist.
        """
        try:
            response = self.http_client.call(
                url=self._url(f'requests/{request_id}'),
                method='GET',
                params=self._params(),
            )
            return _parse_date_fields(_pluck_data(response.json()))

        except ApifyApiError as exc:
            _catch_not_found_or_throw(exc)

        return None

    def update_request(self, request: Dict, *, forefront: Optional[bool] = None) -> Dict:
        """Update a request in the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/request/update-request

        Args:
            request (dict): The updated request
            forefront (bool, optional): Whether to put the updated request in the beginning or the end of the queue

        Returns:
            dict: The updated request
        """
        request_id = request['id']

        request_params = self._params(
            forefront=forefront,
            clientKey=self.client_key,
        )

        response = self.http_client.call(
            url=self._url(f'requests/{request_id}'),
            method='PUT',
            json=request,
            params=request_params,
        )

        return _parse_date_fields(_pluck_data(response.json()))

    def delete_request(self, request_id: str) -> None:
        """Delete a request from the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/request/delete-request

        Args:
            request_id (str): ID of the request to delete.
        """
        request_params = self._params(
            clientKey=self.client_key,
        )

        self.http_client.call(
            url=self._url(f'requests/{request_id}'),
            method='DELETE',
            params=request_params,
        )

    def prolong_request_lock(self, request_id: str, *, lock_secs: int, forefront: Optional[bool] = None) -> Dict:
        """Prolong the lock on a request.

        https://docs.apify.com/api/v2#/reference/request-queues/request-lock/prolong-request-lock

        Args:
            request_id (str): ID of the request to prolong the lock
            lock_secs (int): How long to prolong the lock
            forefront (bool, optional): Whether to put the request in the beginning or the end of the queue after lock exppires
        """
        request_params = self._params(
            forefront=forefront,
            lockSecs=lock_secs,
            clientKey=self.client_key,
        )

        response = self.http_client.call(
            url=self._url(f'requests/{request_id}/lock'),
            method='PUT',
            params=request_params,
        )

        return _parse_date_fields(_pluck_data(response.json()))

    def delete_request_lock(self, request_id: str, *, forefront: Optional[bool] = None) -> None:
        """Delete the lock on a request.

        https://docs.apify.com/api/v2#/reference/request-queues/request-lock/delete-request-lock

        Args:
            request_id (str): ID of the request to delete the lock
            forefront (bool, optional): Whether to put the request in the beginning or the end of the queue after lock deleted
        """
        request_params = self._params(
            clientKey=self.client_key,
            forefront=forefront,
        )

        self.http_client.call(
            url=self._url(f'requests/{request_id}/lock'),
            method='DELETE',
            params=request_params,
        )

    @ignore_docs
    def _batch_add_requests(self, requests: List[Dict[str, Any]], *, forefront: Optional[bool] = None) -> Dict:
        """Adds requests to the queue in single batch.

        https://docs.apify.com/api/v2#/reference/request-queues/batch-request-operations/add-requests

        Args:
            requests (List[Dict[str, Any]]): List of the requests to add
            forefront (bool, optional): Whether to add the requests to the head or the end of the queue
        """
        request_params = self._params(
            clientKey=self.client_key,
            forefront=forefront,
        )

        response = self.http_client.call(
            url=self._url('requests/batch'),
            method='POST',
            params=request_params,
            json=requests,
        )
        return _parse_date_fields(_pluck_data(response.json()))

    def batch_add_requests(self, requests: List[Dict[str, Any]], *, forefront: Optional[bool] = None) -> Dict:
        """Adds requests to the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/batch-request-operations/add-requests

        Args:
            requests (List[Dict[str, Any]]): List of the requests to add
            forefront (bool, optional): Whether to add the requests to the head or the end of the queue
        """
        processed_requests = []
        unprocessed_requests = []

        for i in range(0, len(requests), MAX_REQUESTS_PER_BATCH_OPERATION):
            batch = requests[i:i + MAX_REQUESTS_PER_BATCH_OPERATION]
            response = self._batch_add_requests(batch, forefront=forefront)
            processed_requests += response['processedRequests']
            unprocessed_requests += response['unprocessedRequests']

        return {
            'processedRequests': processed_requests,
            'unprocessedRequests': unprocessed_requests
        }

    def batch_delete_requests(self, requests: List[Dict[str, Any]]) -> Dict:
        """Batch-deletes given requests batch from the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/batch-request-operations/delete-requests

        Args:
            requests (List[Dict[str, Any]]): List of the requests to delete
        """
        request_params = self._params(
            clientKey=self.client_key,
        )

        response = self.http_client.call(
            url=self._url('requests/batch'),
            method='DELETE',
            params=request_params,
            json=requests,
        )

        return _parse_date_fields(_pluck_data(response.json()))

    def list_requests(self, *, limit: Optional[int] = None, exclusive_start_id: Optional[str] = None) -> Dict:
        """List requests in the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/request-collection/list-requests

        Args:
            limit (List[Dict[str, Any]]): Number of keys to be returned.
            exclusive_start_id (str, optional): All requests up to this one (including) are skipped from the result
        """
        request_params = self._params(limit=limit, exclusive_start_id=exclusive_start_id, clientKey=self.client_key)

        response = self.http_client.call(
            url=self._url('requests'),
            method='GET',
            params=request_params,
        )

        return _parse_date_fields(_pluck_data(response.json()))


class RequestQueueClientAsync(ResourceClientAsync):
    """Async sub-client for manipulating a single request queue."""

    @ignore_docs
    def __init__(self, *args: Any, client_key: Optional[str] = None, **kwargs: Any) -> None:
        """Initialize the RequestQueueClientAsync.

        Args:
            client_key (str, optional): A unique identifier of the client accessing the request queue
        """
        resource_path = kwargs.pop('resource_path', 'request-queues')
        super().__init__(*args, resource_path=resource_path, **kwargs)
        self.client_key = client_key

    async def get(self) -> Optional[Dict]:
        """Retrieve the request queue.

        https://docs.apify.com/api/v2#/reference/request-queues/queue/get-request-queue

        Returns:
            dict, optional: The retrieved request queue, or None, if it does not exist
        """
        return await self._get()

    async def update(self, *, name: Optional[str] = None) -> Dict:
        """Update the request queue with specified fields.

        https://docs.apify.com/api/v2#/reference/request-queues/queue/update-request-queue

        Args:
            name (str, optional): The new name for the request queue

        Returns:
            dict: The updated request queue
        """
        updated_fields = {
            'name': name,
        }

        return await self._update(_filter_out_none_values_recursively(updated_fields))

    async def delete(self) -> None:
        """Delete the request queue.

        https://docs.apify.com/api/v2#/reference/request-queues/queue/delete-request-queue
        """
        return await self._delete()

    async def list_head(self, *, limit: Optional[int] = None) -> Dict:
        """Retrieve a given number of requests from the beginning of the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/queue-head/get-head

        Args:
            limit (int, optional): How many requests to retrieve

        Returns:
            dict: The desired number of requests from the beginning of the queue.
        """
        request_params = self._params(limit=limit, clientKey=self.client_key)

        response = await self.http_client.call(
            url=self._url('head'),
            method='GET',
            params=request_params,
        )

        return _parse_date_fields(_pluck_data(response.json()))

    async def list_and_lock_head(self, *, lock_secs: int, limit: Optional[int] = None) -> Dict:
        """Retrieve the given number of first requests from the queue and locks them for the given time.

        https://docs.apify.com/api/v2#/reference/request-queues/queue-head-with-locks/get-head-and-lock

        Args:
            lock_secs (int): How long the second request will be locked for
            limit (int, optional): How many requests to retrieve


        Returns:
            dict: The desired number of locked requests from the beginning of the queue.
        """
        request_params = self._params(lockSecs=lock_secs, limit=limit, clientKey=self.client_key)

        response = await self.http_client.call(
            url=self._url('head/lock'),
            method='POST',
            params=request_params,
        )

        return _parse_date_fields(_pluck_data(response.json()))

    async def add_request(self, request: Dict, *, forefront: Optional[bool] = None) -> Dict:
        """Add a request to the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/request-collection/add-request

        Args:
            request (dict): The request to add to the queue
            forefront (bool, optional): Whether to add the request to the head or the end of the queue

        Returns:
            dict: The added request.
        """
        request_params = self._params(
            forefront=forefront,
            clientKey=self.client_key,
        )

        response = await self.http_client.call(
            url=self._url('requests'),
            method='POST',
            json=request,
            params=request_params,
        )

        return _parse_date_fields(_pluck_data(response.json()))

    async def get_request(self, request_id: str) -> Optional[Dict]:
        """Retrieve a request from the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/request/get-request

        Args:
            request_id (str): ID of the request to retrieve

        Returns:
            dict, optional: The retrieved request, or None, if it did not exist.
        """
        try:
            response = await self.http_client.call(
                url=self._url(f'requests/{request_id}'),
                method='GET',
                params=self._params(),
            )
            return _parse_date_fields(_pluck_data(response.json()))

        except ApifyApiError as exc:
            _catch_not_found_or_throw(exc)

        return None

    async def update_request(self, request: Dict, *, forefront: Optional[bool] = None) -> Dict:
        """Update a request in the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/request/update-request

        Args:
            request (dict): The updated request
            forefront (bool, optional): Whether to put the updated request in the beginning or the end of the queue

        Returns:
            dict: The updated request
        """
        request_id = request['id']

        request_params = self._params(
            forefront=forefront,
            clientKey=self.client_key,
        )

        response = await self.http_client.call(
            url=self._url(f'requests/{request_id}'),
            method='PUT',
            json=request,
            params=request_params,
        )

        return _parse_date_fields(_pluck_data(response.json()))

    async def delete_request(self, request_id: str) -> None:
        """Delete a request from the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/request/delete-request

        Args:
            request_id (str): ID of the request to delete.
        """
        request_params = self._params(
            clientKey=self.client_key,
        )

        await self.http_client.call(
            url=self._url(f'requests/{request_id}'),
            method='DELETE',
            params=request_params,
        )

    async def prolong_request_lock(self, request_id: str, *, lock_secs: int, forefront: Optional[bool] = None) -> Dict:
        """Prolong the lock on a request.

        https://docs.apify.com/api/v2#/reference/request-queues/request-lock/prolong-request-lock

        Args:
            request_id (str): ID of the request to prolong the lock
            lock_secs (int): How long to prolong the lock
            forefront (bool, optional): Whether to put the request in the beginning or the end of the queue after lock exppires
        """
        request_params = self._params(
            forefront=forefront,
            lockSecs=lock_secs,
            clientKey=self.client_key,
        )

        response = await self.http_client.call(
            url=self._url(f'requests/{request_id}/lock'),
            method='PUT',
            params=request_params,
        )

        return _parse_date_fields(_pluck_data(response.json()))

    async def delete_request_lock(self, request_id: str, *, forefront: Optional[bool] = None) -> None:
        """Delete the lock on a request.

        https://docs.apify.com/api/v2#/reference/request-queues/request-lock/delete-request-lock

        Args:
            request_id (str): ID of the request to delete the lock
            forefront (bool, optional): Whether to put the request in the beginning or the end of the queue after lock deleted
        """
        request_params = self._params(
            clientKey=self.client_key,
            forefront=forefront,
        )

        await self.http_client.call(
            url=self._url(f'requests/{request_id}/lock'),
            method='DELETE',
            params=request_params,
        )

    @ignore_docs
    async def _batch_add_requests(self, requests: List[Dict[str, Any]], *, forefront: Optional[bool] = None) -> Dict:
        """Adds requests to the queue in single batch.

        https://docs.apify.com/api/v2#/reference/request-queues/batch-request-operations/add-requests

        Args:
            requests (List[Dict[str, Any]]): List of the requests to add
            forefront (bool, optional): Whether to add the requests to the head or the end of the queue
        """
        request_params = self._params(
            clientKey=self.client_key,
            forefront=forefront,
        )

        response = await self.http_client.call(
            url=self._url('requests/batch'),
            method='POST',
            params=request_params,
            json=requests,
        )
        return _parse_date_fields(_pluck_data(response.json()))

    @ignore_docs
    async def _batch_add_requests_with_retries(
        self,
        requests: List[Dict[str, Any]],
        *,
        forefront: Optional[bool] = None,
        max_unprocessed_requests_retries: int = DEFAULT_UNPROCESSED_RETRIES_BATCH_ADD_REQUESTS,
        min_delay_between_unprocessed_requests_retries_millis: int = DEFAULT_MIN_DELAY_BETWEEN_UNPROCESSED_REQUESTS_RETRIES_MILLIS,
    ) -> Dict:
        # Keep track of the requests that remain to be processed (in parameter format)
        remaining_requests = requests[:]
        # Keep track of the requests that have been processed (in api format)
        processed_requests = []
        # The requests we have not been able to process in the last call
        # ie. those we have not been able to process at all
        unprocessed_requests = []

        for i in range(max_unprocessed_requests_retries + 1):
            try:
                response = await self._batch_add_requests(remaining_requests, forefront=forefront)
                processed_requests.extend(response['processedRequests'])
                unprocessed_requests = response['unprocessedRequests']

                processed_requests_unique_keys = set(
                    req['uniqueKey'] for req in processed_requests
                )
                remaining_requests = [
                    req for req in requests
                    if req['uniqueKey'] not in processed_requests_unique_keys
                ]

                if len(remaining_requests) == 0:
                    break

            except Exception as err:
                print(f'Error adding requests to queue: {err}')
                # When something fails and http client does not retry, the remaining requests are treated as unprocessed.
                # This ensures that this method does not throw and keeps the signature.
                processed_requests_unique_keys = set(
                    req['uniqueKey'] for req in processed_requests
                )
                unprocessed_requests = [
                    req for req in requests
                    if req['uniqueKey'] not in processed_requests_unique_keys
                ]

                break

            delay_millis = int(
                (1 + random.random()) * (2 ** i) * min_delay_between_unprocessed_requests_retries_millis
            )
            await asyncio.sleep(delay_millis / 1000)

        return {
            'processedRequests': processed_requests,
            'unprocessedRequests': unprocessed_requests
        }

    async def batch_add_requests(
        self,
        requests: List[Dict[str, Any]],
        *,
        forefront: Optional[bool] = None,
        max_unprocessed_requests_retries: int = DEFAULT_UNPROCESSED_RETRIES_BATCH_ADD_REQUESTS,
        min_delay_between_unprocessed_requests_retries_millis: int = DEFAULT_MIN_DELAY_BETWEEN_UNPROCESSED_REQUESTS_RETRIES_MILLIS,
        max_parallel: int = DEFAULT_PARALLEL_BATCH_ADD_REQUESTS,
    ) -> Dict:
        """Adds requests to the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/batch-request-operations/add-requests

        Args:
            requests (List[Dict[str, Any]]): List of the requests to add
            forefront (bool, optional): Whether to add the requests to the head or the end of the queue
            max_unprocessed_requests_retries (int, optional): How many times to retry adding unprocessed requests
            min_delay_between_unprocessed_requests_retries_millis (int, optional): How long to wait between retries
        """
        processed_requests = []
        unprocessed_requests = []

        for i in range(0, len(requests), MAX_REQUESTS_PER_BATCH_OPERATION):
            awaitable_in_parallel = []
            batch = requests[i:i + MAX_REQUESTS_PER_BATCH_OPERATION]
            awaitable_in_parallel.append(self._batch_add_requests(
                batch,
                forefront=forefront,
                max_unprocessed_requests_retries=max_unprocessed_requests_retries,
                min_delay_between_unprocessed_requests_retries_millis=min_delay_between_unprocessed_requests_retries_millis,
            ))
            if len(awaitable_in_parallel) >= max_parallel or len(batch) < MAX_REQUESTS_PER_BATCH_OPERATION:
                individual_results = await asyncio.gather(*awaitable_in_parallel)
                for result in individual_results:
                    processed_requests.extend(result.get('processedRequests', []))
                    unprocessed_requests.extend(result.get('unprocessedRequests', []))
                awaitable_in_parallel = []

        return {
            'processedRequests': processed_requests,
            'unprocessedRequests': unprocessed_requests
        }

    async def batch_delete_requests(self, requests: List[Dict[str, Any]]) -> Dict:
        """Batch-deletes given requests batch from the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/batch-request-operations/delete-requests

        Args:
            requests (List[Dict[str, Any]]): List of the requests to delete
        """
        request_params = self._params(
            clientKey=self.client_key,
        )

        response = await self.http_client.call(
            url=self._url('requests/batch'),
            method='DELETE',
            params=request_params,
            json=requests,
        )
        return _parse_date_fields(_pluck_data(response.json()))

    async def list_requests(self, *, limit: Optional[int] = None, exclusive_start_id: Optional[str] = None) -> Dict:
        """List requests in the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/request-collection/list-requests

        Args:
            limit (List[Dict[str, Any]]): Number of keys to be returned.
            exclusive_start_id (str, optional): All requests up to this one (including) are skipped from the result
        """
        request_params = self._params(limit=limit, exclusive_start_id=exclusive_start_id, clientKey=self.client_key)

        response = await self.http_client.call(
            url=self._url('requests'),
            method='GET',
            params=request_params,
        )

        return _parse_date_fields(_pluck_data(response.json()))
