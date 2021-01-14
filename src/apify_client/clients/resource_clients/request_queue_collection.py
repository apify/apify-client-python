from typing import Any, Dict, Optional

from ..base.resource_collection_client import ResourceCollectionClient


class RequestQueueCollectionClient(ResourceCollectionClient):
    """Sub-client for manipulating request queues."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the RequestQueueCollectionClient with the passed arguments."""
        super().__init__(*args, resource_path='request-queues', **kwargs)

    def list(self, *, unnamed: Optional[bool] = None, limit: Optional[int] = None, offset: Optional[int] = None, desc: Optional[bool] = None) -> Dict:
        """List the available request queues.

        https://docs.apify.com/api/v2#/reference/request-queues/queue-collection/get-list-of-request-queues

        Args:
            unnamed (bool): Whether to include unnamed request queues in the list
            limit (int): How many request queues to retrieve
            offset (int): What request queue to include as first when retrieving the list
            desc (bool): Whether to sort therequest queues in descending order based on their modification date

        Returns:
            The list of available request queues matching the specified filters.
        """
        return self._list(unnamed=unnamed, limit=limit, offset=offset, desc=desc)

    def get_or_create(self, *, name: str = '') -> Dict:
        """Retrieve a named request queue, or create a new one when it doesn't exist.

        https://docs.apify.com/api/v2#/reference/request-queues/queue-collection/create-request-queue

        Args:
            name (str): The name of the request queue to retrieve or create.

        Returns:
            The retrieved request queue.
        """
        return self._get_or_create(name=name)
