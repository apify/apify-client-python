from typing import Any, Optional

from ..._utils import ListPage, _make_async_docs
from ..base import ResourceCollectionClient, ResourceCollectionClientAsync


class WebhookDispatchCollectionClient(ResourceCollectionClient):
    """Sub-client for listing webhook dispatches."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the WebhookDispatchCollectionClient."""
        resource_path = kwargs.pop('resource_path', 'webhook-dispatches')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def list(
        self,
        *,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        desc: Optional[bool] = None,
    ) -> ListPage:
        """List all webhook dispatches of a user.

        https://docs.apify.com/api/v2#/reference/webhook-dispatches/webhook-dispatches-collection/get-list-of-webhook-dispatches

        Args:
            limit (int, optional): How many webhook dispatches to retrieve
            offset (int, optional): What webhook dispatch to include as first when retrieving the list
            desc (bool, optional): Whether to sort the webhook dispatches in descending order based on the date of their creation

        Returns:
            ListPage: The retrieved webhook dispatches of a user
        """
        return self._list(limit=limit, offset=offset, desc=desc)


class WebhookDispatchCollectionClientAsync(ResourceCollectionClientAsync):
    """Async sub-client for listing webhook dispatches."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the WebhookDispatchCollectionClientAsync."""
        resource_path = kwargs.pop('resource_path', 'webhook-dispatches')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    @_make_async_docs(src=WebhookDispatchCollectionClient.list)
    async def list(
        self,
        *,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        desc: Optional[bool] = None,
    ) -> ListPage:
        return await self._list(limit=limit, offset=offset, desc=desc)
