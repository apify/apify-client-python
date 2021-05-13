from typing import Any, Dict, Optional

from ..._utils import ListPage
from ..base import ResourceCollectionClient


class KeyValueStoreCollectionClient(ResourceCollectionClient):
    """Sub-client for manipulating key-value stores."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the KeyValueStoreCollectionClient with the passed arguments."""
        resource_path = kwargs.pop('resource_path', 'key-value-stores')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def list(
        self,
        *,
        unnamed: Optional[bool] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        desc: Optional[bool] = None,
    ) -> ListPage:
        """List the available key-value stores.

        https://docs.apify.com/api/v2#/reference/key-value-stores/store-collection/get-list-of-key-value-stores

        Args:
            unnamed (bool, optional): Whether to include unnamed key-value stores in the list
            limit (int, optional): How many key-value stores to retrieve
            offset (int, optional): What key-value store to include as first when retrieving the list
            desc (bool, optional): Whether to sort the key-value stores in descending order based on their modification date

        Returns:
            ListPage: The list of available key-value stores matching the specified filters.
        """
        return self._list(unnamed=unnamed, limit=limit, offset=offset, desc=desc)

    def get_or_create(self, *, name: Optional[str] = None) -> Dict:
        """Retrieve a named key-value store, or create a new one when it doesn't exist.

        https://docs.apify.com/api/v2#/reference/key-value-stores/store-collection/create-key-value-store

        Args:
            name (str, optional): The name of the key-value store to retrieve or create.

        Returns:
            dict: The retrieved or newly-created key-value store.
        """
        return self._get_or_create(name=name)
