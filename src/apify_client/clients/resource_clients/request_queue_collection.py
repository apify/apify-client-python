from typing import Any

from ..base.resource_collection_client import ResourceCollectionClient


class RequestQueueCollectionClient(ResourceCollectionClient):
    """Sub-client for manipulating request queues."""
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes the RequestQueueCollectionClient with the passed arguments."""
        super().__init__(*args, resource_path='request-queues', **kwargs)

    def list(self, *, unnamed: bool = None, limit: int = None, offset: int = None, desc: bool = None) -> Any:
        """Lists the available request queues.

        Args:
            unnamed (bool): Whether to include unnamed request queues in the list
            limit (int): How many request queues to retrieve
            offset (int): What request queue to include as first when retrieving the list
            desc (bool): Whether to sort therequest queues in descending order based on their modification date

        Returns:
            The list of available request queues matching the specified filters.
        """
        return self._list(unnamed=unnamed, limit=limit, offset=offset, desc=desc)

    def get_or_create(self, *, name: str = '') -> Any:
        """Retrieves a named request queue, or creates a new one when it doesn't exist.

        Args:
            name (str): The name of the request queue to retrieve or create.

        Returns:
            The retrieved request queue.
        """
        return self._get_or_create(name=name)
