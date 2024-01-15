from __future__ import annotations

from typing import TYPE_CHECKING, Any

from apify_shared.utils import filter_out_none_values_recursively, ignore_docs

from apify_client.clients.base import ResourceCollectionClient, ResourceCollectionClientAsync

if TYPE_CHECKING:
    from apify_shared.models import ListPage


class DatasetCollectionClient(ResourceCollectionClient):
    """Sub-client for manipulating datasets."""

    @ignore_docs
    def __init__(self: DatasetCollectionClient, *args: Any, **kwargs: Any) -> None:
        """Initialize the DatasetCollectionClient with the passed arguments."""
        resource_path = kwargs.pop('resource_path', 'datasets')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def list(
        self: DatasetCollectionClient,
        *,
        unnamed: bool | None = None,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
    ) -> ListPage[dict]:
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

    def get_or_create(self: DatasetCollectionClient, *, name: str | None = None, schema: dict | None = None) -> dict:
        """Retrieve a named dataset, or create a new one when it doesn't exist.

        https://docs.apify.com/api/v2#/reference/datasets/dataset-collection/create-dataset

        Args:
            name (str, optional): The name of the dataset to retrieve or create.
            schema (dict, optional): The schema of the dataset

        Returns:
            dict: The retrieved or newly-created dataset.
        """
        return self._get_or_create(name=name, resource=filter_out_none_values_recursively({'schema': schema}))


class DatasetCollectionClientAsync(ResourceCollectionClientAsync):
    """Async sub-client for manipulating datasets."""

    @ignore_docs
    def __init__(self: DatasetCollectionClientAsync, *args: Any, **kwargs: Any) -> None:
        """Initialize the DatasetCollectionClientAsync with the passed arguments."""
        resource_path = kwargs.pop('resource_path', 'datasets')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def list(
        self: DatasetCollectionClientAsync,
        *,
        unnamed: bool | None = None,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
    ) -> ListPage[dict]:
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

    async def get_or_create(
        self: DatasetCollectionClientAsync,
        *,
        name: str | None = None,
        schema: dict | None = None,
    ) -> dict:
        """Retrieve a named dataset, or create a new one when it doesn't exist.

        https://docs.apify.com/api/v2#/reference/datasets/dataset-collection/create-dataset

        Args:
            name (str, optional): The name of the dataset to retrieve or create.
            schema (dict, optional): The schema of the dataset

        Returns:
            dict: The retrieved or newly-created dataset.
        """
        return await self._get_or_create(name=name, resource=filter_out_none_values_recursively({'schema': schema}))
