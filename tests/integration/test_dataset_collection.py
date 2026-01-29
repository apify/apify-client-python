"""Unified tests for dataset collection (sync + async)."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from apify_client import ApifyClient, ApifyClientAsync
    from apify_client._models import Dataset, ListOfDatasets

import uuid

from .conftest import maybe_await


async def test_datasets_list(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing datasets."""
    result = await maybe_await(client.datasets().list(limit=10))
    datasets_page = cast('ListOfDatasets', result)

    assert datasets_page is not None
    assert datasets_page.items is not None
    assert isinstance(datasets_page.items, list)


async def test_datasets_list_pagination(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing datasets with pagination."""
    result = await maybe_await(client.datasets().list(limit=5, offset=0))
    datasets_page = cast('ListOfDatasets', result)

    assert datasets_page is not None
    assert datasets_page.items is not None
    assert isinstance(datasets_page.items, list)


async def test_datasets_get_or_create(client: ApifyClient | ApifyClientAsync) -> None:
    """Test get_or_create for datasets."""
    unique_name = f'test-dataset-{uuid.uuid4().hex[:8]}'

    # Create new dataset
    result = await maybe_await(client.datasets().get_or_create(name=unique_name))
    dataset = cast('Dataset', result)
    assert dataset is not None
    assert dataset.name == unique_name

    # Get same dataset again (should return existing)
    result2 = await maybe_await(client.datasets().get_or_create(name=unique_name))
    same_dataset = cast('Dataset', result2)
    assert same_dataset.id == dataset.id

    # Cleanup
    await maybe_await(client.dataset(dataset.id).delete())
