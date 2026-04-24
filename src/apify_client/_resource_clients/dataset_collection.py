from __future__ import annotations

from typing import TYPE_CHECKING, Any

from apify_client._docs import docs_group
from apify_client._iterable_list import (
    AwaitableAsyncIterable,
    IterableListOfDatasets,
    build_awaitable_async_iterable_offset,
    build_iterable_offset,
)
from apify_client._models import Dataset, DatasetResponse, StorageOwnership
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync

if TYPE_CHECKING:
    from apify_client._models import DatasetListItem
    from apify_client._types import Timeout


@docs_group('Resource clients')
class DatasetCollectionClient(ResourceClient):
    """Sub-client for the dataset collection.

    Provides methods to manage the dataset collection, e.g. list or create datasets. Obtain an instance via an
    appropriate method on the `ApifyClient` class.
    """

    def __init__(
        self,
        *,
        resource_path: str = 'datasets',
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
        ownership: StorageOwnership | None = None,
        timeout: Timeout = 'medium',
    ) -> IterableListOfDatasets:
        """List the available datasets.

        The returned page also supports iteration: `for item in client.list(...)` yields individual datasets
        and transparently fetches further pages from the API.

        https://docs.apify.com/api/v2#/reference/datasets/dataset-collection/get-list-of-datasets

        Args:
            unnamed: Whether to include unnamed datasets in the list.
            limit: How many datasets to retrieve.
            offset: What dataset to include as first when retrieving the list.
            desc: Whether to sort the datasets in descending order based on their modification date.
            ownership: Filter by ownership. 'ownedByMe' returns only user's own datasets,
                'sharedWithMe' returns only datasets shared with the user.
            timeout: Timeout for the API HTTP request.

        Returns:
            The list of available datasets matching the specified filters.
        """

        def _callback(**kwargs: Any) -> IterableListOfDatasets:
            result = self._list(timeout=timeout, unnamed=unnamed, ownership=ownership, **kwargs)
            return IterableListOfDatasets.model_validate(result.get('data') if isinstance(result, dict) else result)

        return build_iterable_offset(_callback, limit=limit, offset=offset, desc=desc)

    def get_or_create(
        self,
        *,
        name: str | None = None,
        schema: dict | None = None,
        timeout: Timeout = 'short',
    ) -> Dataset:
        """Retrieve a named dataset, or create a new one when it doesn't exist.

        https://docs.apify.com/api/v2#/reference/datasets/dataset-collection/create-dataset

        Args:
            name: The name of the dataset to retrieve or create.
            schema: The schema of the dataset.
            timeout: Timeout for the API HTTP request.

        Returns:
            The retrieved or newly-created dataset.
        """
        result = self._get_or_create(timeout=timeout, name=name, resource_fields={'schema': schema})
        return DatasetResponse.model_validate(result).data


@docs_group('Resource clients')
class DatasetCollectionClientAsync(ResourceClientAsync):
    """Sub-client for the dataset collection.

    Provides methods to manage the dataset collection, e.g. list or create datasets. Obtain an instance via an
    appropriate method on the `ApifyClientAsync` class.
    """

    def __init__(
        self,
        *,
        resource_path: str = 'datasets',
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
        ownership: StorageOwnership | None = None,
        timeout: Timeout = 'medium',
    ) -> AwaitableAsyncIterable[IterableListOfDatasets, DatasetListItem]:
        """List the available datasets.

        The returned page also supports iteration: `for item in client.list(...)` yields individual datasets
        and transparently fetches further pages from the API.

        https://docs.apify.com/api/v2#/reference/datasets/dataset-collection/get-list-of-datasets

        Args:
            unnamed: Whether to include unnamed datasets in the list.
            limit: How many datasets to retrieve.
            offset: What dataset to include as first when retrieving the list.
            desc: Whether to sort the datasets in descending order based on their modification date.
            ownership: Filter by ownership. 'ownedByMe' returns only user's own datasets,
                'sharedWithMe' returns only datasets shared with the user.
            timeout: Timeout for the API HTTP request.

        Returns:
            The list of available datasets matching the specified filters.
        """

        async def _callback(**kwargs: Any) -> IterableListOfDatasets:
            result = await self._list(timeout=timeout, unnamed=unnamed, ownership=ownership, **kwargs)
            return IterableListOfDatasets.model_validate(result.get('data') if isinstance(result, dict) else result)

        return build_awaitable_async_iterable_offset(_callback, limit=limit, offset=offset, desc=desc)

    async def get_or_create(
        self,
        *,
        name: str | None = None,
        schema: dict | None = None,
        timeout: Timeout = 'short',
    ) -> Dataset:
        """Retrieve a named dataset, or create a new one when it doesn't exist.

        https://docs.apify.com/api/v2#/reference/datasets/dataset-collection/create-dataset

        Args:
            name: The name of the dataset to retrieve or create.
            schema: The schema of the dataset.
            timeout: Timeout for the API HTTP request.

        Returns:
            The retrieved or newly-created dataset.
        """
        result = await self._get_or_create(timeout=timeout, name=name, resource_fields={'schema': schema})
        return DatasetResponse.model_validate(result).data
