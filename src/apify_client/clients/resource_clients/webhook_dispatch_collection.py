from __future__ import annotations

from typing import TYPE_CHECKING, Any

from apify_shared.utils import ignore_docs

from apify_client.clients.base import ResourceCollectionClient, ResourceCollectionClientAsync

if TYPE_CHECKING:
    from apify_shared.models import ListPage


class WebhookDispatchCollectionClient(ResourceCollectionClient):
    """Sub-client for listing webhook dispatches."""

    @ignore_docs
    def __init__(self: WebhookDispatchCollectionClient, *args: Any, **kwargs: Any) -> None:
        """Initialize the WebhookDispatchCollectionClient."""
        resource_path = kwargs.pop('resource_path', 'webhook-dispatches')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def list(
        self: WebhookDispatchCollectionClient,
        *,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
    ) -> ListPage[dict]:
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

    @ignore_docs
    def __init__(self: WebhookDispatchCollectionClientAsync, *args: Any, **kwargs: Any) -> None:
        """Initialize the WebhookDispatchCollectionClientAsync."""
        resource_path = kwargs.pop('resource_path', 'webhook-dispatches')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def list(
        self: WebhookDispatchCollectionClientAsync,
        *,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
    ) -> ListPage[dict]:
        """List all webhook dispatches of a user.

        https://docs.apify.com/api/v2#/reference/webhook-dispatches/webhook-dispatches-collection/get-list-of-webhook-dispatches

        Args:
            limit (int, optional): How many webhook dispatches to retrieve
            offset (int, optional): What webhook dispatch to include as first when retrieving the list
            desc (bool, optional): Whether to sort the webhook dispatches in descending order based on the date of their creation

        Returns:
            ListPage: The retrieved webhook dispatches of a user
        """
        return await self._list(limit=limit, offset=offset, desc=desc)
