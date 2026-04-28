from __future__ import annotations

from typing import TYPE_CHECKING, Any

from apify_client._docs import docs_group
from apify_client._iterable_list_page import (
    IterableListPage,
    IterableListPageAsync,
    build_iterable_list_page,
    build_iterable_list_page_async, _LazyTask
)
from apify_client._models_generated import ListOfWebhookDispatches, WebhookDispatchList
from apify_client._pagination_classes import ListPageOfWebhookDispatches, PaginatedPage, \
    ListPageOfWebhookDispatchesAsync
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync

if TYPE_CHECKING:
    from apify_client._models_generated import WebhookDispatch
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
    ) -> ListPageOfWebhookDispatches:
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

        def _callback(**kwargs: Any) -> ListOfWebhookDispatches:
            result = self._list(timeout=timeout, **kwargs)
            return WebhookDispatchList.model_validate(result).data

        first_page = _callback(limit=limit, offset=offset, desc=desc)
        get_iterator = build_iterable_list_page(_callback,first_page, limit=limit, offset=offset, desc=desc)

        return ListPageOfWebhookDispatches(_get_iterator=get_iterator,
                                           items=first_page.items,
                                           count=first_page.count,
                                           offset=first_page.offset,
                                           limit=first_page.limit,
                                           total=first_page.total,
                                           desc=first_page.desc)


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
    ) -> ListPageOfWebhookDispatchesAsync:
        """List all webhook dispatches of a user.

        The returned page also supports iteration: `async for item in client.list(...)` yields individual
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

        async def _callback(**kwargs: Any) -> PaginatedPage[WebhookDispatch]:
            result = await self._list(timeout=timeout, **kwargs)
            data = WebhookDispatchList.model_validate(result).data
            return PaginatedPage(items=data.items, count=data.count, offset=data.offset, desc=data.desc, total=data.total, limit=data.limit)

        fetch_first_page = _LazyTask(_callback(limit=limit, offset=offset, desc=desc))
        get_async_iterator = build_iterable_list_page_async(_callback, fetch_first_page,
                                                limit=limit, offset=offset, desc=desc)

        return ListPageOfWebhookDispatchesAsync(_awaitable_first_page=fetch_first_page, _get_async_iterator=get_async_iterator)
