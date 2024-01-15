from __future__ import annotations

from typing import TYPE_CHECKING, Any

from apify_shared.utils import ignore_docs

from apify_client.clients.base import ResourceCollectionClient, ResourceCollectionClientAsync

if TYPE_CHECKING:
    from apify_shared.models import ListPage


class StoreCollectionClient(ResourceCollectionClient):
    """Sub-client for Apify store."""

    @ignore_docs
    def __init__(self: StoreCollectionClient, *args: Any, **kwargs: Any) -> None:
        """Initialize the StoreCollectionClient."""
        resource_path = kwargs.pop('resource_path', 'store')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def list(
        self: StoreCollectionClient,
        *,
        limit: int | None = None,
        offset: int | None = None,
        search: str | None = None,
        sort_by: str | None = None,
        category: str | None = None,
        username: str | None = None,
        pricing_model: str | None = None,
    ) -> ListPage[dict]:
        """List Actors in Apify store.

        https://docs.apify.com/api/v2/#/reference/store/store-actors-collection/get-list-of-actors-in-store

        Args:
            limit (int, optional): How many Actors to list
            offset (int, optional): What Actor to include as first when retrieving the list
            search (str, optional): String to search by. The search runs on the following fields: title, name, description, username, readme.
            sort_by (str, optional): Specifies the field by which to sort the results.
            category (str, optional): Filter by this category
            username (str, optional): Filter by this username
            pricing_model (str, optional): Filter by this pricing model

        Returns:
            ListPage: The list of available tasks matching the specified filters.
        """
        return self._list(
            limit=limit,
            offset=offset,
            search=search,
            sortBy=sort_by,
            category=category,
            username=username,
            pricingModel=pricing_model,
        )


class StoreCollectionClientAsync(ResourceCollectionClientAsync):
    """Async sub-client for Apify store."""

    @ignore_docs
    def __init__(self: StoreCollectionClientAsync, *args: Any, **kwargs: Any) -> None:
        """Initialize the StoreCollectionClientAsync."""
        resource_path = kwargs.pop('resource_path', 'store')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def list(
        self: StoreCollectionClientAsync,
        *,
        limit: int | None = None,
        offset: int | None = None,
        search: str | None = None,
        sort_by: str | None = None,
        category: str | None = None,
        username: str | None = None,
        pricing_model: str | None = None,
    ) -> ListPage[dict]:
        """List Actors in Apify store.

        https://docs.apify.com/api/v2/#/reference/store/store-actors-collection/get-list-of-actors-in-store

        Args:
            limit (int, optional): How many Actors to list
            offset (int, optional): What Actor to include as first when retrieving the list
            search (str, optional): String to search by. The search runs on the following fields: title, name, description, username, readme.
            sort_by (str, optional): Specifies the field by which to sort the results.
            category (str, optional): Filter by this category
            username (str, optional): Filter by this username
            pricing_model (str, optional): Filter by this pricing model

        Returns:
            ListPage: The list of available tasks matching the specified filters.
        """
        return await self._list(
            limit=limit,
            offset=offset,
            search=search,
            sortBy=sort_by,
            category=category,
            username=username,
            pricingModel=pricing_model,
        )
