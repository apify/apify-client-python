from __future__ import annotations

from typing import Any

from apify_client._models import CreateDatasetResponse, Dataset, GetListOfDatasetsResponse, ListOfDatasets
from apify_client._resource_clients.base import ResourceCollectionClient, ResourceCollectionClientAsync
from apify_client._utils import filter_out_none_values_recursively, response_to_dict


class DatasetCollectionClient(ResourceCollectionClient):
    """Sub-client for manipulating datasets."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'datasets')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def list(
        self,
        *,
        unnamed: bool | None = None,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
    ) -> ListOfDatasets:
        """List the available datasets.

        https://docs.apify.com/api/v2#/reference/datasets/dataset-collection/get-list-of-datasets

        Args:
            unnamed: Whether to include unnamed datasets in the list.
            limit: How many datasets to retrieve.
            offset: What dataset to include as first when retrieving the list.
            desc: Whether to sort the datasets in descending order based on their modification date.

        Returns:
            The list of available datasets matching the specified filters.
        """
        response = self.http_client.call(
            url=self._url(),
            method='GET',
            params=self._params(unnamed=unnamed, limit=limit, offset=offset, desc=desc),
        )
        data = response_to_dict(response)
        return GetListOfDatasetsResponse.model_validate(data).data

    def get_or_create(self, *, name: str | None = None, schema: dict | None = None) -> Dataset:
        """Retrieve a named dataset, or create a new one when it doesn't exist.

        https://docs.apify.com/api/v2#/reference/datasets/dataset-collection/create-dataset

        Args:
            name: The name of the dataset to retrieve or create.
            schema: The schema of the dataset.

        Returns:
            The retrieved or newly-created dataset.
        """
        result = self._get_or_create(name=name, resource=filter_out_none_values_recursively({'schema': schema}))
        return CreateDatasetResponse.model_validate(result).data


class DatasetCollectionClientAsync(ResourceCollectionClientAsync):
    """Async sub-client for manipulating datasets."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'datasets')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def list(
        self,
        *,
        unnamed: bool | None = None,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
    ) -> ListOfDatasets:
        """List the available datasets.

        https://docs.apify.com/api/v2#/reference/datasets/dataset-collection/get-list-of-datasets

        Args:
            unnamed: Whether to include unnamed datasets in the list.
            limit: How many datasets to retrieve.
            offset: What dataset to include as first when retrieving the list.
            desc: Whether to sort the datasets in descending order based on their modification date.

        Returns:
            The list of available datasets matching the specified filters.
        """
        response = await self.http_client.call(
            url=self._url(),
            method='GET',
            params=self._params(unnamed=unnamed, limit=limit, offset=offset, desc=desc),
        )
        data = response_to_dict(response)
        return GetListOfDatasetsResponse.model_validate(data).data

    async def get_or_create(
        self,
        *,
        name: str | None = None,
        schema: dict | None = None,
    ) -> Dataset:
        """Retrieve a named dataset, or create a new one when it doesn't exist.

        https://docs.apify.com/api/v2#/reference/datasets/dataset-collection/create-dataset

        Args:
            name: The name of the dataset to retrieve or create.
            schema: The schema of the dataset.

        Returns:
            The retrieved or newly-created dataset.
        """
        result = await self._get_or_create(name=name, resource=filter_out_none_values_recursively({'schema': schema}))
        return CreateDatasetResponse.model_validate(result).data
