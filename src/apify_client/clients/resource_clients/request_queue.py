from typing import Any, Dict, Optional

from ..._errors import ApifyApiError
from ..._utils import _catch_not_found_or_throw, _parse_date_fields, _pluck_data
from ..base import ResourceClient


class RequestQueueClient(ResourceClient):
    """Sub-client for manipulating a single request queue."""

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
        updated_fields = {}
        if name is not None:
            updated_fields['name'] = name

        return self._update(updated_fields)

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
