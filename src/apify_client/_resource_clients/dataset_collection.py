from __future__ import annotations

from typing import Any

from apify_client._docs import docs_group
from apify_client._models import Dataset, DatasetResponse, ListOfDatasets, ListOfDatasetsResponse
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync


@docs_group('Resource clients')
class DatasetCollectionClient(ResourceClient):
    """Sub-client for the dataset collection.

    Provides methods to manage the dataset collection, e.g. list or create datasets. Obtain an instance via an
    appropriate method on the `ApifyClient` class.
    """

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
        result = self._list(unnamed=unnamed, limit=limit, offset=offset, desc=desc)
        return ListOfDatasetsResponse.model_validate(result).data

    def get_or_create(self, *, name: str | None = None, schema: dict | None = None) -> Dataset:
        """Retrieve a named dataset, or create a new one when it doesn't exist.

        https://docs.apify.com/api/v2#/reference/datasets/dataset-collection/create-dataset

        Args:
            name: The name of the dataset to retrieve or create.
            schema: The schema of the dataset.

        Returns:
            The retrieved or newly-created dataset.
        """
        result = self._get_or_create(name=name, resource_fields={'schema': schema})
        return DatasetResponse.model_validate(result).data


@docs_group('Resource clients')
class DatasetCollectionClientAsync(ResourceClientAsync):
    """Sub-client for the dataset collection.

    Provides methods to manage the dataset collection, e.g. list or create datasets. Obtain an instance via an
    appropriate method on the `ApifyClientAsync` class.
    """

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
        result = await self._list(unnamed=unnamed, limit=limit, offset=offset, desc=desc)
        return ListOfDatasetsResponse.model_validate(result).data

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
        result = await self._get_or_create(name=name, resource_fields={'schema': schema})
        return DatasetResponse.model_validate(result).data
