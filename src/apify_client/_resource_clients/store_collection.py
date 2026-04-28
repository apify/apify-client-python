from __future__ import annotations

from typing import TYPE_CHECKING, Any

from apify_client._docs import docs_group
from apify_client._models_generated import ListOfActorsInStoreResponse
from apify_client._pagination import (
    _LazyTask,
    build_get_iterator,
    build_get_iterator_async,
)
from apify_client._pagination_classes import (
    ListPageOfStoreActors,
    ListPageOfStoreActorsAsync,
    PageOfItems,
)
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync

if TYPE_CHECKING:
    from apify_client._models_generated import StoreListActor
    from apify_client._types import Timeout


@docs_group('Resource clients')
class StoreCollectionClient(ResourceClient):
    """Sub-client for the Apify store collection.

    Provides methods to browse the Apify store, e.g. list available Actors. Obtain an instance via an appropriate
    method on the `ApifyClient` class.
    """

    def __init__(
        self,
        *,
        resource_path: str = 'store',
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
        search: str | None = None,
        sort_by: str | None = None,
        category: str | None = None,
        username: str | None = None,
        pricing_model: str | None = None,
        timeout: Timeout = 'medium',
    ) -> ListPageOfStoreActors:
        """List Actors in Apify store.

        The returned page also supports iteration: `for item in client.list(...)` yields individual Actors
        from the store and transparently fetches further pages from the API.

        https://docs.apify.com/api/v2/#/reference/store/store-actors-collection/get-list-of-actors-in-store

        Args:
            limit: How many Actors to list.
            offset: What Actor to include as first when retrieving the list.
            search: String to search by. The search runs on the following fields: title, name, description, username,
                readme.
            sort_by: Specifies the field by which to sort the results.
            category: Filter by this category.
            username: Filter by this username.
            pricing_model: Filter by this pricing model.
            timeout: Timeout for the API HTTP request.

        Returns:
            The list of available Actors matching the specified filters.
        """

        def _callback(**kwargs: Any) -> PageOfItems[StoreListActor]:
            result = self._list(
                timeout=timeout,
                search=search,
                sortBy=sort_by,
                category=category,
                username=username,
                pricingModel=pricing_model,
                **kwargs,
            )
            data = ListOfActorsInStoreResponse.model_validate(result).data
            return PageOfItems(
                items=data.items,
                count=data.count,
                limit=data.limit,
                total=data.total,
                offset=data.offset,
                desc=data.desc,
            )

        first_page = _callback(limit=limit, offset=offset)
        get_iterator = build_get_iterator(_callback, first_page, limit=limit, offset=offset)

        return ListPageOfStoreActors(
            _get_iterator=get_iterator,
            items=first_page.items,
            count=first_page.count,
            limit=first_page.limit,
            total=first_page.total,
            offset=first_page.offset,
            desc=first_page.desc,
        )


@docs_group('Resource clients')
class StoreCollectionClientAsync(ResourceClientAsync):
    """Sub-client for the Apify store collection.

    Provides methods to browse the Apify store, e.g. list available Actors. Obtain an instance via an appropriate
    method on the `ApifyClientAsync` class.
    """

    def __init__(
        self,
        *,
        resource_path: str = 'store',
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
        search: str | None = None,
        sort_by: str | None = None,
        category: str | None = None,
        username: str | None = None,
        pricing_model: str | None = None,
        timeout: Timeout = 'medium',
    ) -> ListPageOfStoreActorsAsync:
        """List Actors in Apify store.

        The returned page also supports iteration: `async for item in client.list(...)` yields individual Actors
        from the store and transparently fetches further pages from the API.

        https://docs.apify.com/api/v2/#/reference/store/store-actors-collection/get-list-of-actors-in-store

        Args:
            limit: How many Actors to list.
            offset: What Actor to include as first when retrieving the list.
            search: String to search by. The search runs on the following fields: title, name, description, username,
                readme.
            sort_by: Specifies the field by which to sort the results.
            category: Filter by this category.
            username: Filter by this username.
            pricing_model: Filter by this pricing model.
            timeout: Timeout for the API HTTP request.

        Returns:
            The list of available Actors matching the specified filters.
        """

        async def _callback(**kwargs: Any) -> PageOfItems[StoreListActor]:
            result = await self._list(
                timeout=timeout,
                search=search,
                sortBy=sort_by,
                category=category,
                username=username,
                pricingModel=pricing_model,
                **kwargs,
            )
            data = ListOfActorsInStoreResponse.model_validate(result).data
            return PageOfItems(
                items=data.items,
                count=data.count,
                limit=data.limit,
                total=data.total,
                offset=data.offset,
                desc=data.desc,
            )

        fetch_first_page = _LazyTask(_callback(limit=limit, offset=offset))
        get_async_iterator = build_get_iterator_async(_callback, fetch_first_page, limit=limit, offset=offset)

        return ListPageOfStoreActorsAsync(
            _awaitable_first_page=fetch_first_page,
            _get_async_iterator=get_async_iterator,
        )
