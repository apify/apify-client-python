from __future__ import annotations

from typing import Any

from apify_client._docs import docs_group
from apify_client._models import WebhookDispatch, WebhookDispatchResponse
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync


@docs_group('Resource clients')
class WebhookDispatchClient(ResourceClient):
    """Sub-client for querying information about a webhook dispatch."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'webhook-dispatches')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def get(self) -> WebhookDispatch | None:
        """Retrieve the webhook dispatch.

        https://docs.apify.com/api/v2#/reference/webhook-dispatches/webhook-dispatch-object/get-webhook-dispatch

        Returns:
            The retrieved webhook dispatch, or None if it does not exist.
        """
        result = self._get()
        if result is None:
            return None
        return WebhookDispatchResponse.model_validate(result).data


@docs_group('Resource clients')
class WebhookDispatchClientAsync(ResourceClientAsync):
    """Async sub-client for querying information about a webhook dispatch."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'webhook-dispatches')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def get(self) -> WebhookDispatch | None:
        """Retrieve the webhook dispatch.

        https://docs.apify.com/api/v2#/reference/webhook-dispatches/webhook-dispatch-object/get-webhook-dispatch

        Returns:
            The retrieved webhook dispatch, or None if it does not exist.
        """
        result = await self._get()
        if result is None:
            return None
        return WebhookDispatchResponse.model_validate(result).data
