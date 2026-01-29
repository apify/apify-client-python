from __future__ import annotations

from typing import Any

from apify_client._models import GetListOfActorsInStoreResponse, ListOfStoreActors
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync
from apify_client._utils import response_to_dict


class StoreCollectionClient(ResourceClient):
    """Sub-client for Apify store."""

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
        response = self._http_client.call(
            url=self._build_url(),
            method='GET',
            params=self._build_params(
                limit=limit,
                offset=offset,
                search=search,
                sortBy=sort_by,
                category=category,
                username=username,
                pricingModel=pricing_model,
            ),
        )
        response_as_dict = response_to_dict(response)
        return GetListOfActorsInStoreResponse.model_validate(response_as_dict).data


class StoreCollectionClientAsync(ResourceClientAsync):
    """Async sub-client for Apify store."""

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
        response = await self._http_client.call(
            url=self._build_url(),
            method='GET',
            params=self._build_params(
                limit=limit,
                offset=offset,
                search=search,
                sortBy=sort_by,
                category=category,
                username=username,
                pricingModel=pricing_model,
            ),
        )
        response_as_dict = response_to_dict(response)
        return GetListOfActorsInStoreResponse.model_validate(response_as_dict).data
