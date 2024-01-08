from __future__ import annotations

from typing import Any

from apify_shared.utils import filter_out_none_values_recursively, ignore_docs, parse_date_fields

from apify_client._errors import ApifyApiError
from apify_client._utils import catch_not_found_or_throw, pluck_data
from apify_client.clients.base import ResourceClient, ResourceClientAsync


class RequestQueueClient(ResourceClient):
    """Sub-client for manipulating a single request queue."""

    @ignore_docs
    def __init__(  # noqa: D417
        self: RequestQueueClient,
        *args: Any,
        client_key: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the RequestQueueClient.

        Args:
            client_key (str, optional): A unique identifier of the client accessing the request queue
        """
        resource_path = kwargs.pop('resource_path', 'request-queues')
        super().__init__(*args, resource_path=resource_path, **kwargs)
        self.client_key = client_key

    def get(self: RequestQueueClient) -> dict | None:
        """Retrieve the request queue.

        https://docs.apify.com/api/v2#/reference/request-queues/queue/get-request-queue

        Returns:
            dict, optional: The retrieved request queue, or None, if it does not exist
        """
        return self._get()

    def update(self: RequestQueueClient, *, name: str | None = None) -> dict:
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

        return self._update(filter_out_none_values_recursively(updated_fields))

    def delete(self: RequestQueueClient) -> None:
        """Delete the request queue.

        https://docs.apify.com/api/v2#/reference/request-queues/queue/delete-request-queue
        """
        return self._delete()

    def list_head(self: RequestQueueClient, *, limit: int | None = None) -> dict:
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

        return parse_date_fields(pluck_data(response.json()))

    def list_and_lock_head(self: RequestQueueClient, *, lock_secs: int, limit: int | None = None) -> dict:
        """Retrieve a given number of unlocked requests from the beginning of the queue and lock them for a given time.

        https://docs.apify.com/api/v2#/reference/request-queues/queue-head-with-locks/get-head-and-lock

        Args:
            lock_secs (int): How long the requests will be locked for, in seconds
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

        return parse_date_fields(pluck_data(response.json()))

    def add_request(self: RequestQueueClient, request: dict, *, forefront: bool | None = None) -> dict:
        """Add a request to the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/request-collection/add-request

        Args:
            request (dict): The request to add to the queue
            forefront (bool, optional): Whether to add the request to the head or the end of the queue

        Returns:
            dict: The added request.
        """
        request_params = self._params(forefront=forefront, clientKey=self.client_key)

        response = self.http_client.call(
            url=self._url('requests'),
            method='POST',
            json=request,
            params=request_params,
        )

        return parse_date_fields(pluck_data(response.json()))

    def get_request(self: RequestQueueClient, request_id: str) -> dict | None:
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
            return parse_date_fields(pluck_data(response.json()))

        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

        return None

    def update_request(self: RequestQueueClient, request: dict, *, forefront: bool | None = None) -> dict:
        """Update a request in the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/request/update-request

        Args:
            request (dict): The updated request
            forefront (bool, optional): Whether to put the updated request in the beginning or the end of the queue

        Returns:
            dict: The updated request
        """
        request_id = request['id']

        request_params = self._params(forefront=forefront, clientKey=self.client_key)

        response = self.http_client.call(
            url=self._url(f'requests/{request_id}'),
            method='PUT',
            json=request,
            params=request_params,
        )

        return parse_date_fields(pluck_data(response.json()))

    def delete_request(self: RequestQueueClient, request_id: str) -> None:
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

    def prolong_request_lock(
        self: RequestQueueClient,
        request_id: str,
        *,
        forefront: bool | None = None,
        lock_secs: int,
    ) -> dict:
        """Prolong the lock on a request.

        https://docs.apify.com/api/v2#/reference/request-queues/request-lock/prolong-request-lock

        Args:
            request_id (str): ID of the request to prolong the lock
            forefront (bool, optional): Whether to put the request in the beginning or the end of the queue after lock expires
            lock_secs (int): By how much to prolong the lock, in seconds
        """
        request_params = self._params(clientKey=self.client_key, forefront=forefront, lockSecs=lock_secs)

        response = self.http_client.call(
            url=self._url(f'requests/{request_id}/lock'),
            method='PUT',
            params=request_params,
        )

        return parse_date_fields(pluck_data(response.json()))

    def delete_request_lock(self: RequestQueueClient, request_id: str, *, forefront: bool | None = None) -> None:
        """Delete the lock on a request.

        https://docs.apify.com/api/v2#/reference/request-queues/request-lock/delete-request-lock

        Args:
            request_id (str): ID of the request to delete the lock
            forefront (bool, optional): Whether to put the request in the beginning or the end of the queue after the lock is deleted
        """
        request_params = self._params(clientKey=self.client_key, forefront=forefront)

        self.http_client.call(
            url=self._url(f'requests/{request_id}/lock'),
            method='DELETE',
            params=request_params,
        )

    def batch_add_requests(
        self: RequestQueueClient,
        requests: list[dict],
        *,
        forefront: bool | None = None,
    ) -> dict:
        """Add requests to the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/batch-request-operations/add-requests

        Args:
            requests (list[dict]): list of the requests to add
            forefront (bool, optional): Whether to add the requests to the head or the end of the queue
        """
        request_params = self._params(clientKey=self.client_key, forefront=forefront)

        response = self.http_client.call(
            url=self._url('requests/batch'),
            method='POST',
            params=request_params,
            json=requests,
        )
        return parse_date_fields(pluck_data(response.json()))

    def batch_delete_requests(self: RequestQueueClient, requests: list[dict]) -> dict:
        """Delete given requests from the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/batch-request-operations/delete-requests

        Args:
            requests (list[dict]): list of the requests to delete
        """
        request_params = self._params(clientKey=self.client_key)

        response = self.http_client.call(
            url=self._url('requests/batch'),
            method='DELETE',
            params=request_params,
            json=requests,
        )

        return parse_date_fields(pluck_data(response.json()))

    def list_requests(
        self: RequestQueueClient,
        *,
        limit: int | None = None,
        exclusive_start_id: str | None = None,
    ) -> dict:
        """List requests in the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/request-collection/list-requests

        Args:
            limit (int, optional): How many requests to retrieve
            exclusive_start_id (str, optional): All requests up to this one (including) are skipped from the result
        """
        request_params = self._params(limit=limit, exclusive_start_id=exclusive_start_id, clientKey=self.client_key)

        response = self.http_client.call(
            url=self._url('requests'),
            method='GET',
            params=request_params,
        )

        return parse_date_fields(pluck_data(response.json()))


class RequestQueueClientAsync(ResourceClientAsync):
    """Async sub-client for manipulating a single request queue."""

    @ignore_docs
    def __init__(  # noqa: D417
        self: RequestQueueClientAsync,
        *args: Any,
        client_key: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the RequestQueueClientAsync.

        Args:
            client_key (str, optional): A unique identifier of the client accessing the request queue
        """
        resource_path = kwargs.pop('resource_path', 'request-queues')
        super().__init__(*args, resource_path=resource_path, **kwargs)
        self.client_key = client_key

    async def get(self: RequestQueueClientAsync) -> dict | None:
        """Retrieve the request queue.

        https://docs.apify.com/api/v2#/reference/request-queues/queue/get-request-queue

        Returns:
            dict, optional: The retrieved request queue, or None, if it does not exist
        """
        return await self._get()

    async def update(self: RequestQueueClientAsync, *, name: str | None = None) -> dict:
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

        return await self._update(filter_out_none_values_recursively(updated_fields))

    async def delete(self: RequestQueueClientAsync) -> None:
        """Delete the request queue.

        https://docs.apify.com/api/v2#/reference/request-queues/queue/delete-request-queue
        """
        return await self._delete()

    async def list_head(self: RequestQueueClientAsync, *, limit: int | None = None) -> dict:
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

        return parse_date_fields(pluck_data(response.json()))

    async def list_and_lock_head(self: RequestQueueClientAsync, *, lock_secs: int, limit: int | None = None) -> dict:
        """Retrieve a given number of unlocked requests from the beginning of the queue and lock them for a given time.

        https://docs.apify.com/api/v2#/reference/request-queues/queue-head-with-locks/get-head-and-lock

        Args:
            lock_secs (int): How long the requests will be locked for, in seconds
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

        return parse_date_fields(pluck_data(response.json()))

    async def add_request(self: RequestQueueClientAsync, request: dict, *, forefront: bool | None = None) -> dict:
        """Add a request to the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/request-collection/add-request

        Args:
            request (dict): The request to add to the queue
            forefront (bool, optional): Whether to add the request to the head or the end of the queue

        Returns:
            dict: The added request.
        """
        request_params = self._params(forefront=forefront, clientKey=self.client_key)

        response = await self.http_client.call(
            url=self._url('requests'),
            method='POST',
            json=request,
            params=request_params,
        )

        return parse_date_fields(pluck_data(response.json()))

    async def get_request(self: RequestQueueClientAsync, request_id: str) -> dict | None:
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
            return parse_date_fields(pluck_data(response.json()))

        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

        return None

    async def update_request(self: RequestQueueClientAsync, request: dict, *, forefront: bool | None = None) -> dict:
        """Update a request in the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/request/update-request

        Args:
            request (dict): The updated request
            forefront (bool, optional): Whether to put the updated request in the beginning or the end of the queue

        Returns:
            dict: The updated request
        """
        request_id = request['id']

        request_params = self._params(forefront=forefront, clientKey=self.client_key)

        response = await self.http_client.call(
            url=self._url(f'requests/{request_id}'),
            method='PUT',
            json=request,
            params=request_params,
        )

        return parse_date_fields(pluck_data(response.json()))

    async def delete_request(self: RequestQueueClientAsync, request_id: str) -> None:
        """Delete a request from the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/request/delete-request

        Args:
            request_id (str): ID of the request to delete.
        """
        request_params = self._params(clientKey=self.client_key)

        await self.http_client.call(
            url=self._url(f'requests/{request_id}'),
            method='DELETE',
            params=request_params,
        )

    async def prolong_request_lock(
        self: RequestQueueClientAsync,
        request_id: str,
        *,
        forefront: bool | None = None,
        lock_secs: int,
    ) -> dict:
        """Prolong the lock on a request.

        https://docs.apify.com/api/v2#/reference/request-queues/request-lock/prolong-request-lock

        Args:
            request_id (str): ID of the request to prolong the lock
            forefront (bool, optional): Whether to put the request in the beginning or the end of the queue after lock expires
            lock_secs (int): By how much to prolong the lock, in seconds
        """
        request_params = self._params(clientKey=self.client_key, forefront=forefront, lockSecs=lock_secs)

        response = await self.http_client.call(
            url=self._url(f'requests/{request_id}/lock'),
            method='PUT',
            params=request_params,
        )

        return parse_date_fields(pluck_data(response.json()))

    async def delete_request_lock(
        self: RequestQueueClientAsync,
        request_id: str,
        *,
        forefront: bool | None = None,
    ) -> None:
        """Delete the lock on a request.

        https://docs.apify.com/api/v2#/reference/request-queues/request-lock/delete-request-lock

        Args:
            request_id (str): ID of the request to delete the lock
            forefront (bool, optional): Whether to put the request in the beginning or the end of the queue after the lock is deleted
        """
        request_params = self._params(clientKey=self.client_key, forefront=forefront)

        await self.http_client.call(
            url=self._url(f'requests/{request_id}/lock'),
            method='DELETE',
            params=request_params,
        )

    async def batch_add_requests(
        self: RequestQueueClientAsync,
        requests: list[dict],
        *,
        forefront: bool | None = None,
    ) -> dict:
        """Add requests to the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/batch-request-operations/add-requests

        Args:
            requests (list[dict]): list of the requests to add
            forefront (bool, optional): Whether to add the requests to the head or the end of the queue
        """
        request_params = self._params(clientKey=self.client_key, forefront=forefront)

        response = await self.http_client.call(
            url=self._url('requests/batch'),
            method='POST',
            params=request_params,
            json=requests,
        )
        return parse_date_fields(pluck_data(response.json()))

    async def batch_delete_requests(self: RequestQueueClientAsync, requests: list[dict]) -> dict:
        """Delete given requests from the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/batch-request-operations/delete-requests

        Args:
            requests (list[dict]): list of the requests to delete
        """
        request_params = self._params(clientKey=self.client_key)

        response = await self.http_client.call(
            url=self._url('requests/batch'),
            method='DELETE',
            params=request_params,
            json=requests,
        )
        return parse_date_fields(pluck_data(response.json()))

    async def list_requests(
        self: RequestQueueClientAsync,
        *,
        limit: int | None = None,
        exclusive_start_id: str | None = None,
    ) -> dict:
        """List requests in the queue.

        https://docs.apify.com/api/v2#/reference/request-queues/request-collection/list-requests

        Args:
            limit (int, optional): How many requests to retrieve
            exclusive_start_id (str, optional): All requests up to this one (including) are skipped from the result
        """
        request_params = self._params(limit=limit, exclusive_start_id=exclusive_start_id, clientKey=self.client_key)

        response = await self.http_client.call(
            url=self._url('requests'),
            method='GET',
            params=request_params,
        )

        return parse_date_fields(pluck_data(response.json()))
