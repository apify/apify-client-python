from typing import Any, Dict, Optional

from ..base.resource_client import ResourceClient


class WebhookDispatchClient(ResourceClient):
    """Sub-client for querying information about a webhook dispatch."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the WebhookDispatchClient."""
        super().__init__(*args, resource_path='webhook-dispatches', **kwargs)

    def get(self) -> Optional[Dict]:
        """Retrieve the webhook dispatch.

        https://docs.apify.com/api/v2#/reference/webhook-dispatches/webhook-dispatch-object/get-webhook-dispatch

        Returns:
            The retrieved webhook dispatch
        """
        return self._get()
