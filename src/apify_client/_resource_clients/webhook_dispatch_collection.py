from __future__ import annotations

from typing import Any

from apify_client._models import ListOfWebhookDispatches, WebhookDispatchList
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync


class WebhookDispatchCollectionClient(ResourceClient):
    """Sub-client for listing webhook dispatches."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'webhook-dispatches')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
    ) -> ListOfWebhookDispatches | None:
        """List all webhook dispatches of a user.

        https://docs.apify.com/api/v2#/reference/webhook-dispatches/webhook-dispatches-collection/get-list-of-webhook-dispatches

        Args:
            limit: How many webhook dispatches to retrieve.
            offset: What webhook dispatch to include as first when retrieving the list.
            desc: Whether to sort the webhook dispatches in descending order based on the date of their creation.

        Returns:
            The retrieved webhook dispatches of a user.
        """
        result = self._list(limit=limit, offset=offset, desc=desc)
        return WebhookDispatchList.model_validate(result).data


class WebhookDispatchCollectionClientAsync(ResourceClientAsync):
    """Async sub-client for listing webhook dispatches."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'webhook-dispatches')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
    ) -> ListOfWebhookDispatches | None:
        """List all webhook dispatches of a user.

        https://docs.apify.com/api/v2#/reference/webhook-dispatches/webhook-dispatches-collection/get-list-of-webhook-dispatches

        Args:
            limit: How many webhook dispatches to retrieve.
            offset: What webhook dispatch to include as first when retrieving the list.
            desc: Whether to sort the webhook dispatches in descending order based on the date of their creation.

        Returns:
            The retrieved webhook dispatches of a user.
        """
        result = await self._list(limit=limit, offset=offset, desc=desc)
        return WebhookDispatchList.model_validate(result).data
