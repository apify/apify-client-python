from __future__ import annotations

from typing import Any

from apify_client._models import GetWebhookDispatchResponse, WebhookDispatch
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync
from apify_client._utils import catch_not_found_or_throw, response_to_dict
from apify_client.errors import ApifyApiError


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
        try:
            response = self.http_client.call(
                url=self.url,
                method='GET',
                params=self.params,
            )
            result = response_to_dict(response)
            return GetWebhookDispatchResponse.model_validate(result).data
        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)
            return None


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
        try:
            response = await self.http_client.call(
                url=self.url,
                method='GET',
                params=self.params,
            )
            result = response_to_dict(response)
            return GetWebhookDispatchResponse.model_validate(result).data
        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)
            return None
