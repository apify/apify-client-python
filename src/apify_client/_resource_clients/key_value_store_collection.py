from __future__ import annotations

from typing import TYPE_CHECKING, Any

from apify_client._docs import docs_group
from apify_client._models import (
    KeyValueStore,
    KeyValueStoreResponse,
    ListOfKeyValueStores,
    ListOfKeyValueStoresResponse,
)
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync

if TYPE_CHECKING:
    from apify_client._types import Timeout


@docs_group('Resource clients')
class KeyValueStoreCollectionClient(ResourceClient):
    """Sub-client for the key-value store collection.

    Provides methods to manage the key-value store collection, e.g. list or create key-value stores. Obtain an instance
    via an appropriate method on the `ApifyClient` class.
    """

    def __init__(
        self,
        *,
        resource_path: str = 'key-value-stores',
        **kwargs: Any,
    ) -> None:
        super().__init__(
            resource_path=resource_path,
            **kwargs,
        )

    def list(
        self,
        *,
        unnamed: bool | None = None,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
        timeout: Timeout = 'medium',
    ) -> ListOfKeyValueStores:
        """List the available key-value stores.

        https://docs.apify.com/api/v2#/reference/key-value-stores/store-collection/get-list-of-key-value-stores

        Args:
            unnamed: Whether to include unnamed key-value stores in the list.
            limit: How many key-value stores to retrieve.
            offset: What key-value store to include as first when retrieving the list.
            desc: Whether to sort the key-value stores in descending order based on their modification date.
            timeout: Timeout for the API HTTP request.

        Returns:
            The list of available key-value stores matching the specified filters.
        """
        result = self._list(timeout=timeout, unnamed=unnamed, limit=limit, offset=offset, desc=desc)
        return ListOfKeyValueStoresResponse.model_validate(result).data

    def get_or_create(
        self,
        *,
        name: str | None = None,
        schema: dict | None = None,
        timeout: Timeout = 'short',
    ) -> KeyValueStore:
        """Retrieve a named key-value store, or create a new one when it doesn't exist.

        https://docs.apify.com/api/v2#/reference/key-value-stores/store-collection/create-key-value-store

        Args:
            name: The name of the key-value store to retrieve or create.
            schema: The schema of the key-value store.
            timeout: Timeout for the API HTTP request.

        Returns:
            The retrieved or newly-created key-value store.
        """
        result = self._get_or_create(timeout=timeout, name=name, resource_fields={'schema': schema})
        return KeyValueStoreResponse.model_validate(result).data


@docs_group('Resource clients')
class KeyValueStoreCollectionClientAsync(ResourceClientAsync):
    """Sub-client for the key-value store collection.

    Provides methods to manage the key-value store collection, e.g. list or create key-value stores. Obtain an instance
    via an appropriate method on the `ApifyClientAsync` class.
    """

    def __init__(
        self,
        *,
        resource_path: str = 'key-value-stores',
        **kwargs: Any,
    ) -> None:
        super().__init__(
            resource_path=resource_path,
            **kwargs,
        )

    async def list(
        self,
        *,
        unnamed: bool | None = None,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
        timeout: Timeout = 'medium',
    ) -> ListOfKeyValueStores:
        """List the available key-value stores.

        https://docs.apify.com/api/v2#/reference/key-value-stores/store-collection/get-list-of-key-value-stores

        Args:
            unnamed: Whether to include unnamed key-value stores in the list.
            limit: How many key-value stores to retrieve.
            offset: What key-value store to include as first when retrieving the list.
            desc: Whether to sort the key-value stores in descending order based on their modification date.
            timeout: Timeout for the API HTTP request.

        Returns:
            The list of available key-value stores matching the specified filters.
        """
        result = await self._list(timeout=timeout, unnamed=unnamed, limit=limit, offset=offset, desc=desc)
        return ListOfKeyValueStoresResponse.model_validate(result).data

    async def get_or_create(
        self,
        *,
        name: str | None = None,
        schema: dict | None = None,
        timeout: Timeout = 'short',
    ) -> KeyValueStore:
        """Retrieve a named key-value store, or create a new one when it doesn't exist.

        https://docs.apify.com/api/v2#/reference/key-value-stores/store-collection/create-key-value-store

        Args:
            name: The name of the key-value store to retrieve or create.
            schema: The schema of the key-value store.
            timeout: Timeout for the API HTTP request.

        Returns:
            The retrieved or newly-created key-value store.
        """
        result = await self._get_or_create(timeout=timeout, name=name, resource_fields={'schema': schema})
        return KeyValueStoreResponse.model_validate(result).data
