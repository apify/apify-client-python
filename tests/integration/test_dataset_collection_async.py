from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apify_client import ApifyClientAsync


async def test_datasets_list(apify_client_async: ApifyClientAsync) -> None:
    """Test listing datasets."""
    datasets_page = await apify_client_async.datasets().list(limit=10)

    assert datasets_page is not None
    assert datasets_page.items is not None
    assert isinstance(datasets_page.items, list)


async def test_datasets_list_pagination(apify_client_async: ApifyClientAsync) -> None:
    """Test listing datasets with pagination."""
    datasets_page = await apify_client_async.datasets().list(limit=5, offset=0)

    assert datasets_page is not None
    assert datasets_page.items is not None
    assert isinstance(datasets_page.items, list)


async def test_datasets_get_or_create(apify_client_async: ApifyClientAsync) -> None:
    """Test get_or_create for datasets."""
    unique_name = f'test-dataset-{uuid.uuid4().hex[:8]}'

    # Create new dataset
    dataset = await apify_client_async.datasets().get_or_create(name=unique_name)
    assert dataset is not None
    assert dataset.name == unique_name

    # Get same dataset again (should return existing)
    same_dataset = await apify_client_async.datasets().get_or_create(name=unique_name)
    assert same_dataset.id == dataset.id

    # Cleanup
    await apify_client_async.dataset(dataset.id).delete()
