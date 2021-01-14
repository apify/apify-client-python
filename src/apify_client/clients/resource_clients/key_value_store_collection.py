from typing import Any, Dict, Optional

from ..base.resource_collection_client import ResourceCollectionClient


class KeyValueStoreCollectionClient(ResourceCollectionClient):
    """Sub-client for manipulating key-value stores."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the KeyValueStoreCollectionClient with the passed arguments."""
        super().__init__(*args, resource_path='key-value-stores', **kwargs)

    def list(self, *, unnamed: Optional[bool] = None, limit: Optional[int] = None, offset: Optional[int] = None, desc: Optional[bool] = None) -> Dict:
        """List the available key-value stores.

        https://docs.apify.com/api/v2#/reference/key-value-stores/store-collection/get-list-of-key-value-stores

        Args:
            unnamed: Whether to include unnamed key-value stores in the list
            limit: How many key-value stores to retrieve
            offset: What key-value store to include as first when retrieving the list
            desc: Whether to sort the key-value stores in descending order based on their modification date

        Returns:
            The list of available key-value stores matching the specified filters.
        """
        return self._list(unnamed=unnamed, limit=limit, offset=offset, desc=desc)

    def get_or_create(self, *, name: str = '') -> Dict:
        """Retrieve a named key-value store, or create a new one when it doesn't exist.

        https://docs.apify.com/api/v2#/reference/key-value-stores/store-collection/create-key-value-store

        Args:
            name: The name of the key-value store to retrieve or create.

        Returns:
            The retrieved key-value store.
        """
        return self._get_or_create(name=name)
