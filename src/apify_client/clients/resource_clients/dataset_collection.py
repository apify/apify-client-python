from typing import Any, Dict, Optional

from ..base.resource_collection_client import ResourceCollectionClient


class DatasetCollectionClient(ResourceCollectionClient):
    """Sub-client for manipulating datasets."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the DatasetCollectionClient with the passed arguments."""
        super().__init__(*args, resource_path='datasets', **kwargs)

    def list(self, *, unnamed: Optional[bool] = None, limit: Optional[int] = None, offset: Optional[int] = None, desc: Optional[bool] = None) -> Dict:
        """List the available datasets.

        https://docs.apify.com/api/v2#/reference/datasets/dataset-collection/get-list-of-datasets

        Args:
            unnamed (bool, optional): Whether to include unnamed datasets in the list
            limit (int, optional): How many datasets to retrieve
            offset (int, optional): What dataset to include as first when retrieving the list
            desc (bool, optional): Whether to sort the datasets in descending order based on their modification date

        Returns:
            The list of available datasets matching the specified filters.
        """
        return self._list(unnamed=unnamed, limit=limit, offset=offset, desc=desc)

    def get_or_create(self, *, name: str = '') -> Dict:
        """Retrieve a named dataset, or creates a new one when it doesn't exist.

        https://docs.apify.com/api/v2#/reference/datasets/dataset-collection/create-dataset

        Args:
            name (str, optional): The name of the dataset to retrieve or create.

        Returns:
            The retrieved dataset.
        """
        return self._get_or_create(name=name)
