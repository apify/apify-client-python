from typing import Any

from ..base.resource_collection_client import ResourceCollectionClient


class DatasetCollectionClient(ResourceCollectionClient):
    """Sub-client for manipulating datasets."""
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes the DatasetCollectionClient with the passed arguments."""
        super().__init__(*args, resource_path='datasets', **kwargs)

    def list(self, *, unnamed: bool = None, limit: int = None, offset: int = None, desc: bool = None) -> Any:
        """Lists the available datasets.

        Args:
            unnamed: Whether to include unnamed datasets in the list
            limit: How many datasets to retrieve
            offset: What dataset to include as first when retrieving the list
            desc: Whether to sort the datasets in descending order based on their modification date

        Returns:
            The list of available datasets matching the specified filters.
        """
        return self._list(unnamed=unnamed, limit=limit, offset=offset, desc=desc)

    def get_or_create(self, *, name: str = '') -> Any:
        """Retrieves a named dataset, or creates a new one when it doesn't exist.

        Args:
            name: The name of the dataset to retrieve or create.

        Returns:
            The retrieved dataset.
        """
        return self._get_or_create(name=name)
