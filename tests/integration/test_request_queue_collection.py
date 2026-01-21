from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apify_client import ApifyClient


def test_request_queues_list(apify_client: ApifyClient) -> None:
    """Test listing request queues."""
    rq_page = apify_client.request_queues().list(limit=10)

    assert rq_page is not None
    assert rq_page.items is not None
    assert isinstance(rq_page.items, list)


def test_request_queues_list_pagination(apify_client: ApifyClient) -> None:
    """Test listing request queues with pagination."""
    rq_page = apify_client.request_queues().list(limit=5, offset=0)

    assert rq_page is not None
    assert rq_page.items is not None
    assert isinstance(rq_page.items, list)


def test_request_queues_get_or_create(apify_client: ApifyClient) -> None:
    """Test get_or_create for request queues."""
    unique_name = f'test-rq-{uuid.uuid4().hex[:8]}'

    # Create new RQ
    rq = apify_client.request_queues().get_or_create(name=unique_name)
    assert rq is not None
    assert rq.name == unique_name

    # Get same RQ again (should return existing)
    same_rq = apify_client.request_queues().get_or_create(name=unique_name)
    assert same_rq.id == rq.id

    # Cleanup
    apify_client.request_queue(rq.id).delete()
