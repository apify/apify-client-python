from __future__ import annotations

from typing import TYPE_CHECKING, Any

from apify_client._docs import docs_group
from apify_client._models import ListOfWebhookDispatches, WebhookDispatchList
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync

if TYPE_CHECKING:
    from apify_client._types import Timeout


@docs_group('Resource clients')
class WebhookDispatchCollectionClient(ResourceClient):
    """Sub-client for the webhook dispatch collection.

    Provides methods to manage webhook dispatches, e.g. list them. Obtain an instance via an appropriate method on the
    `ApifyClient` class.
    """

    def __init__(
        self,
        *,
        resource_path: str = 'webhook-dispatches',
        **kwargs: Any,
    ) -> None:
        super().__init__(
            resource_path=resource_path,
            **kwargs,
        )

    def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
        timeout: Timeout = 'medium',
    ) -> ListOfWebhookDispatches | None:
        """List all webhook dispatches of a user.

        https://docs.apify.com/api/v2#/reference/webhook-dispatches/webhook-dispatches-collection/get-list-of-webhook-dispatches

        Args:
            limit: How many webhook dispatches to retrieve.
            offset: What webhook dispatch to include as first when retrieving the list.
            desc: Whether to sort the webhook dispatches in descending order based on the date of their creation.
            timeout: Timeout for the API HTTP request.

        Returns:
            The retrieved webhook dispatches of a user.
        """
        result = self._list(timeout=timeout, limit=limit, offset=offset, desc=desc)
        return WebhookDispatchList.model_validate(result).data


@docs_group('Resource clients')
class WebhookDispatchCollectionClientAsync(ResourceClientAsync):
    """Sub-client for the webhook dispatch collection.

    Provides methods to manage webhook dispatches, e.g. list them. Obtain an instance via an appropriate method on the
    `ApifyClientAsync` class.
    """

    def __init__(
        self,
        *,
        resource_path: str = 'webhook-dispatches',
        **kwargs: Any,
    ) -> None:
        super().__init__(
            resource_path=resource_path,
            **kwargs,
        )

    async def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
        timeout: Timeout = 'medium',
    ) -> ListOfWebhookDispatches | None:
        """List all webhook dispatches of a user.

        https://docs.apify.com/api/v2#/reference/webhook-dispatches/webhook-dispatches-collection/get-list-of-webhook-dispatches

        Args:
            limit: How many webhook dispatches to retrieve.
            offset: What webhook dispatch to include as first when retrieving the list.
            desc: Whether to sort the webhook dispatches in descending order based on the date of their creation.
            timeout: Timeout for the API HTTP request.

        Returns:
            The retrieved webhook dispatches of a user.
        """
        result = await self._list(timeout=timeout, limit=limit, offset=offset, desc=desc)
        return WebhookDispatchList.model_validate(result).data
