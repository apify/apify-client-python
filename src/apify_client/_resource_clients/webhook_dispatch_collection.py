from __future__ import annotations

from typing import TYPE_CHECKING, Any

from apify_client._docs import docs_group
from apify_client._iterable_list import (
    AwaitableAsyncIterable,
    IterableListOfWebhookDispatches,
    build_awaitable_async_iterable_offset,
    build_iterable_offset,
)
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync

if TYPE_CHECKING:
    from apify_client._models import WebhookDispatch
    from apify_client._types import Timeout


_EMPTY_WEBHOOK_DISPATCHES = IterableListOfWebhookDispatches(total=0, offset=0, limit=1, desc=False, count=0, items=[])


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
    ) -> IterableListOfWebhookDispatches:
        """List all webhook dispatches of a user.

        The returned page also supports iteration: `for item in client.list(...)` yields individual
        webhook dispatches and transparently fetches further pages from the API.

        https://docs.apify.com/api/v2#/reference/webhook-dispatches/webhook-dispatches-collection/get-list-of-webhook-dispatches

        Args:
            limit: How many webhook dispatches to retrieve.
            offset: What webhook dispatch to include as first when retrieving the list.
            desc: Whether to sort the webhook dispatches in descending order based on the date of their creation.
            timeout: Timeout for the API HTTP request.

        Returns:
            The retrieved webhook dispatches of a user.
        """

        def _callback(**kwargs: Any) -> IterableListOfWebhookDispatches:
            result = self._list(timeout=timeout, **kwargs)
            return (
                IterableListOfWebhookDispatches.model_validate(
                    result.get('data') if isinstance(result, dict) else result
                )
                or _EMPTY_WEBHOOK_DISPATCHES
            )

        return build_iterable_offset(_callback, limit=limit, offset=offset, desc=desc)


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

    def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
        timeout: Timeout = 'medium',
    ) -> AwaitableAsyncIterable[IterableListOfWebhookDispatches, WebhookDispatch]:
        """List all webhook dispatches of a user.

        The returned page also supports iteration: `for item in client.list(...)` yields individual
        webhook dispatches and transparently fetches further pages from the API.

        https://docs.apify.com/api/v2#/reference/webhook-dispatches/webhook-dispatches-collection/get-list-of-webhook-dispatches

        Args:
            limit: How many webhook dispatches to retrieve.
            offset: What webhook dispatch to include as first when retrieving the list.
            desc: Whether to sort the webhook dispatches in descending order based on the date of their creation.
            timeout: Timeout for the API HTTP request.

        Returns:
            The retrieved webhook dispatches of a user.
        """

        async def _callback(**kwargs: Any) -> IterableListOfWebhookDispatches:
            result = await self._list(timeout=timeout, **kwargs)
            return (
                IterableListOfWebhookDispatches.model_validate(
                    result.get('data') if isinstance(result, dict) else result
                )
                or _EMPTY_WEBHOOK_DISPATCHES
            )

        return build_awaitable_async_iterable_offset(_callback, limit=limit, offset=offset, desc=desc)
