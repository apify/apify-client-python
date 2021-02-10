from typing import Any, Dict, Optional

from ..base.resource_collection_client import ResourceCollectionClient


class WebhookDispatchCollectionClient(ResourceCollectionClient):
    """Sub-client for listing webhook dispatches."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the WebhookDispatchCollectionClient."""
        resource_path = kwargs.pop('resource_path', 'webhook-dispatches')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def list(self, *, limit: Optional[int] = None, offset: Optional[int] = None, desc: Optional[bool] = None) -> Dict:
        """List all webhook dispatches of a user.

        https://docs.apify.com/api/v2#/reference/webhook-dispatches/webhook-dispatches-collection/get-list-of-webhook-dispatches
        Args:
            limit: How many webhook dispatches to retrieve
            offset: What webhook dispatch to include as first when retrieving the list
            desc: Whether to sort the webhook dispatches in descending order based on the date of their creation

        Returns:
            The retrieved webhook dispatches of a user
        """
        return self._list(limit=limit, offset=offset, desc=desc)
