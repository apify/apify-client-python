from __future__ import annotations

from typing import Any

from apify_client._docs import docs_group
from apify_client._models import ListOfActorsInStoreResponse, ListOfStoreActors
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync


@docs_group('Resource clients')
class StoreCollectionClient(ResourceClient):
    """Sub-client for the Apify store collection.

    Provides methods to browse the Apify store, e.g. list available Actors. Obtain an instance via an appropriate
    method on the `ApifyClient` class.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'store')
        super().__init__(*args, resource_path=resource_path, **kwargs)

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
    ) -> ListOfStoreActors:
        """List Actors in Apify store.

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

        Returns:
            The list of available Actors matching the specified filters.
        """
        result = self._list(
            limit=limit,
            offset=offset,
            search=search,
            sortBy=sort_by,
            category=category,
            username=username,
            pricingModel=pricing_model,
        )
        return ListOfActorsInStoreResponse.model_validate(result).data


@docs_group('Resource clients')
class StoreCollectionClientAsync(ResourceClientAsync):
    """Sub-client for the Apify store collection.

    Provides methods to browse the Apify store, e.g. list available Actors. Obtain an instance via an appropriate
    method on the `ApifyClientAsync` class.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'store')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        search: str | None = None,
        sort_by: str | None = None,
        category: str | None = None,
        username: str | None = None,
        pricing_model: str | None = None,
    ) -> ListOfStoreActors:
        """List Actors in Apify store.

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

        Returns:
            The list of available Actors matching the specified filters.
        """
        result = await self._list(
            limit=limit,
            offset=offset,
            search=search,
            sortBy=sort_by,
            category=category,
            username=username,
            pricingModel=pricing_model,
        )
        return ListOfActorsInStoreResponse.model_validate(result).data
