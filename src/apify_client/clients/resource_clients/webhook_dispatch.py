from __future__ import annotations

from typing import Any

from apify_shared.utils import ignore_docs

from apify_client.clients.base import ResourceClient, ResourceClientAsync


class WebhookDispatchClient(ResourceClient):
    """Sub-client for querying information about a webhook dispatch."""

    @ignore_docs
    def __init__(self: WebhookDispatchClient, *args: Any, **kwargs: Any) -> None:
        """Initialize the WebhookDispatchClient."""
        resource_path = kwargs.pop('resource_path', 'webhook-dispatches')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def get(self: WebhookDispatchClient) -> dict | None:
        """Retrieve the webhook dispatch.

        https://docs.apify.com/api/v2#/reference/webhook-dispatches/webhook-dispatch-object/get-webhook-dispatch

        Returns:
            dict, optional: The retrieved webhook dispatch, or None if it does not exist
        """
        return self._get()


class WebhookDispatchClientAsync(ResourceClientAsync):
    """Async sub-client for querying information about a webhook dispatch."""

    @ignore_docs
    def __init__(self: WebhookDispatchClientAsync, *args: Any, **kwargs: Any) -> None:
        """Initialize the WebhookDispatchClientAsync."""
        resource_path = kwargs.pop('resource_path', 'webhook-dispatches')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def get(self: WebhookDispatchClientAsync) -> dict | None:
        """Retrieve the webhook dispatch.

        https://docs.apify.com/api/v2#/reference/webhook-dispatches/webhook-dispatch-object/get-webhook-dispatch

        Returns:
            dict, optional: The retrieved webhook dispatch, or None if it does not exist
        """
        return await self._get()
