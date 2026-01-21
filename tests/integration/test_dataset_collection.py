from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apify_client import ApifyClient


def test_datasets_list(apify_client: ApifyClient) -> None:
    """Test listing datasets."""
    datasets_page = apify_client.datasets().list(limit=10)

    assert datasets_page is not None
    assert datasets_page.items is not None
    assert isinstance(datasets_page.items, list)


def test_datasets_list_pagination(apify_client: ApifyClient) -> None:
    """Test listing datasets with pagination."""
    datasets_page = apify_client.datasets().list(limit=5, offset=0)

    assert datasets_page is not None
    assert datasets_page.items is not None
    assert isinstance(datasets_page.items, list)


def test_datasets_get_or_create(apify_client: ApifyClient) -> None:
    """Test get_or_create for datasets."""
    unique_name = f'test-dataset-{uuid.uuid4().hex[:8]}'

    # Create new dataset
    dataset = apify_client.datasets().get_or_create(name=unique_name)
    assert dataset is not None
    assert dataset.name == unique_name

    # Get same dataset again (should return existing)
    same_dataset = apify_client.datasets().get_or_create(name=unique_name)
    assert same_dataset.id == dataset.id

    # Cleanup
    apify_client.dataset(dataset.id).delete()
