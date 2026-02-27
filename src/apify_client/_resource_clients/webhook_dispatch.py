from __future__ import annotations

from typing import Any

from apify_client._docs import docs_group
from apify_client._models import WebhookDispatch, WebhookDispatchResponse
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync


@docs_group('Resource clients')
class WebhookDispatchClient(ResourceClient):
    """Sub-client for managing a specific webhook dispatch.

    Provides methods to manage a specific webhook dispatch, e.g. get its details. Obtain an instance via an appropriate
    method on the `ApifyClient` class.
    """

    def __init__(
        self,
        *,
        resource_id: str,
        resource_path: str = 'webhook-dispatches',
        **kwargs: Any,
    ) -> None:
        super().__init__(
            resource_id=resource_id,
            resource_path=resource_path,
            **kwargs,
        )

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
    """Sub-client for managing a specific webhook dispatch.

    Provides methods to manage a specific webhook dispatch, e.g. get its details. Obtain an instance via an appropriate
    method on the `ApifyClientAsync` class.
    """

    def __init__(
        self,
        *,
        resource_id: str,
        resource_path: str = 'webhook-dispatches',
        **kwargs: Any,
    ) -> None:
        super().__init__(
            resource_id=resource_id,
            resource_path=resource_path,
            **kwargs,
        )

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
