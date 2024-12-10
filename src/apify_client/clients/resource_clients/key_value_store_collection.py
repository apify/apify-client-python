from __future__ import annotations

from typing import TYPE_CHECKING, Any

from apify_shared.utils import filter_out_none_values_recursively, ignore_docs

from apify_client.clients.base import ResourceCollectionClient, ResourceCollectionClientAsync

if TYPE_CHECKING:
    from apify_shared.models import ListPage


class KeyValueStoreCollectionClient(ResourceCollectionClient):
    """Sub-client for manipulating key-value stores."""

    @ignore_docs
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'key-value-stores')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def list(
        self,
        *,
        unnamed: bool | None = None,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
    ) -> ListPage[dict]:
        """List the available key-value stores.

        https://docs.apify.com/api/v2#/reference/key-value-stores/store-collection/get-list-of-key-value-stores

        Args:
            unnamed: Whether to include unnamed key-value stores in the list.
            limit: How many key-value stores to retrieve.
            offset: What key-value store to include as first when retrieving the list.
            desc: Whether to sort the key-value stores in descending order based on their modification date.

        Returns:
            The list of available key-value stores matching the specified filters.
        """
        return self._list(unnamed=unnamed, limit=limit, offset=offset, desc=desc)

    def get_or_create(
        self,
        *,
        name: str | None = None,
        schema: dict | None = None,
    ) -> dict:
        """Retrieve a named key-value store, or create a new one when it doesn't exist.

        https://docs.apify.com/api/v2#/reference/key-value-stores/store-collection/create-key-value-store

        Args:
            name: The name of the key-value store to retrieve or create.
            schema: The schema of the key-value store.

        Returns:
            The retrieved or newly-created key-value store.
        """
        return self._get_or_create(name=name, resource=filter_out_none_values_recursively({'schema': schema}))


class KeyValueStoreCollectionClientAsync(ResourceCollectionClientAsync):
    """Async sub-client for manipulating key-value stores."""

    @ignore_docs
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'key-value-stores')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def list(
        self,
        *,
        unnamed: bool | None = None,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
    ) -> ListPage[dict]:
        """List the available key-value stores.

        https://docs.apify.com/api/v2#/reference/key-value-stores/store-collection/get-list-of-key-value-stores

        Args:
            unnamed: Whether to include unnamed key-value stores in the list.
            limit: How many key-value stores to retrieve.
            offset: What key-value store to include as first when retrieving the list.
            desc: Whether to sort the key-value stores in descending order based on their modification date.

        Returns:
            The list of available key-value stores matching the specified filters.
        """
        return await self._list(unnamed=unnamed, limit=limit, offset=offset, desc=desc)

    async def get_or_create(
        self,
        *,
        name: str | None = None,
        schema: dict | None = None,
    ) -> dict:
        """Retrieve a named key-value store, or create a new one when it doesn't exist.

        https://docs.apify.com/api/v2#/reference/key-value-stores/store-collection/create-key-value-store

        Args:
            name: The name of the key-value store to retrieve or create.
            schema: The schema of the key-value store.

        Returns:
            The retrieved or newly-created key-value store.
        """
        return await self._get_or_create(name=name, resource=filter_out_none_values_recursively({'schema': schema}))
