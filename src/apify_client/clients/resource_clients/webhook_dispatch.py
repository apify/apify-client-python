from typing import Any, Dict, Optional

from ..._utils import _make_async_docs
from ..base import ResourceClient, ResourceClientAsync


class WebhookDispatchClient(ResourceClient):
    """Sub-client for querying information about a webhook dispatch."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the WebhookDispatchClient."""
        resource_path = kwargs.pop('resource_path', 'webhook-dispatches')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def get(self) -> Optional[Dict]:
        """Retrieve the webhook dispatch.

        https://docs.apify.com/api/v2#/reference/webhook-dispatches/webhook-dispatch-object/get-webhook-dispatch

        Returns:
            dict, optional: The retrieved webhook dispatch, or None if it does not exist
        """
        return self._get()


class WebhookDispatchClientAsync(ResourceClientAsync):
    """Async sub-client for querying information about a webhook dispatch."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the WebhookDispatchClientAsync."""
        resource_path = kwargs.pop('resource_path', 'webhook-dispatches')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    @_make_async_docs(src=WebhookDispatchClient.get)
    async def get(self) -> Optional[Dict]:
        return await self._get()
