from __future__ import annotations

from typing import TYPE_CHECKING, Any

from apify_client._docs import docs_group
from apify_client._iterable_list_page import (
    IterableListPage,
    IterableListPageAsync,
    build_iterable_list_page,
    build_iterable_list_page_async,
)
from apify_client._models_generated import ListOfActorsInStoreResponse, ListOfStoreActors
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
    ) -> IterableListPage[StoreListActor]:
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

        def _callback(**kwargs: Any) -> ListOfStoreActors:
            result = self._list(
                timeout=timeout,
                search=search,
                sortBy=sort_by,
                category=category,
                username=username,
                pricingModel=pricing_model,
                **kwargs,
            )
            return ListOfActorsInStoreResponse.model_validate(result).data

        return build_iterable_list_page(_callback, limit=limit, offset=offset)


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
    ) -> IterableListPageAsync[StoreListActor]:
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

        async def _callback(**kwargs: Any) -> ListOfStoreActors:
            result = await self._list(
                timeout=timeout,
                search=search,
                sortBy=sort_by,
                category=category,
                username=username,
                pricingModel=pricing_model,
                **kwargs,
            )
            return ListOfActorsInStoreResponse.model_validate(result).data

        return build_iterable_list_page_async(_callback, limit=limit, offset=offset)
