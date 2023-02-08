from typing import Any, Dict, Optional

from ..._utils import ListPage, _filter_out_none_values_recursively, ignore_docs
from ..base import ResourceCollectionClient, ResourceCollectionClientAsync


class DatasetCollectionClient(ResourceCollectionClient):
    """Sub-client for manipulating datasets."""

    @ignore_docs
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the DatasetCollectionClient with the passed arguments."""
        resource_path = kwargs.pop('resource_path', 'datasets')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def list(
        self,
        *,
        unnamed: Optional[bool] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        desc: Optional[bool] = None,
    ) -> ListPage[Dict]:
        """List the available datasets.

        https://docs.apify.com/api/v2#/reference/datasets/dataset-collection/get-list-of-datasets

        Args:
            unnamed (bool, optional): Whether to include unnamed datasets in the list
            limit (int, optional): How many datasets to retrieve
            offset (int, optional): What dataset to include as first when retrieving the list
            desc (bool, optional): Whether to sort the datasets in descending order based on their modification date

        Returns:
            ListPage: The list of available datasets matching the specified filters.
        """
        return self._list(unnamed=unnamed, limit=limit, offset=offset, desc=desc)

    def get_or_create(self, *, name: Optional[str] = None, schema: Optional[Dict] = None) -> Dict:
        """Retrieve a named dataset, or create a new one when it doesn't exist.

        https://docs.apify.com/api/v2#/reference/datasets/dataset-collection/create-dataset

        Args:
            name (str, optional): The name of the dataset to retrieve or create.
            schema (Dict, optional): The schema of the dataset

        Returns:
            dict: The retrieved or newly-created dataset.
        """
        return self._get_or_create(name=name, resource=_filter_out_none_values_recursively({'schema': schema}))


class DatasetCollectionClientAsync(ResourceCollectionClientAsync):
    """Async sub-client for manipulating datasets."""

    @ignore_docs
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the DatasetCollectionClientAsync with the passed arguments."""
        resource_path = kwargs.pop('resource_path', 'datasets')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def list(
        self,
        *,
        unnamed: Optional[bool] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        desc: Optional[bool] = None,
    ) -> ListPage[Dict]:
        """List the available datasets.

        https://docs.apify.com/api/v2#/reference/datasets/dataset-collection/get-list-of-datasets

        Args:
            unnamed (bool, optional): Whether to include unnamed datasets in the list
            limit (int, optional): How many datasets to retrieve
            offset (int, optional): What dataset to include as first when retrieving the list
            desc (bool, optional): Whether to sort the datasets in descending order based on their modification date

        Returns:
            ListPage: The list of available datasets matching the specified filters.
        """
        return await self._list(unnamed=unnamed, limit=limit, offset=offset, desc=desc)

    async def get_or_create(self, *, name: Optional[str] = None, schema: Optional[Dict] = None) -> Dict:
        """Retrieve a named dataset, or create a new one when it doesn't exist.

        https://docs.apify.com/api/v2#/reference/datasets/dataset-collection/create-dataset

        Args:
            name (str, optional): The name of the dataset to retrieve or create.
            schema (Dict, optional): The schema of the dataset

        Returns:
            dict: The retrieved or newly-created dataset.
        """
        return await self._get_or_create(name=name, resource=_filter_out_none_values_recursively({'schema': schema}))
