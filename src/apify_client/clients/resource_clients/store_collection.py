from typing import Any, Dict, Optional

from apify_shared.models import ListPage
from apify_shared.utils import ignore_docs

from ..base import ResourceCollectionClient, ResourceCollectionClientAsync


class StoreCollectionClient(ResourceCollectionClient):
    """Sub-client for Apify store."""

    @ignore_docs
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the StoreCollectionClient."""
        resource_path = kwargs.pop('resource_path', 'store')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def list(
        self,
        *,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        search: Optional[str] = None,
        sort_by: Optional[str] = None,
        category: Optional[str] = None,
        username: Optional[str] = None,
        pricing_model: Optional[str] = None,
    ) -> ListPage[Dict]:
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
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the StoreCollectionClientAsync."""
        resource_path = kwargs.pop('resource_path', 'store')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def list(
        self,
        *,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        search: Optional[str] = None,
        sort_by: Optional[str] = None,
        category: Optional[str] = None,
        username: Optional[str] = None,
        pricing_model: Optional[str] = None,
    ) -> ListPage[Dict]:
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
