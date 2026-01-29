"""Unified tests for request queue collection (sync + async)."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from apify_client import ApifyClient, ApifyClientAsync
    from apify_client._models import ListOfRequestQueues, RequestQueue

import uuid

from .conftest import maybe_await


async def test_request_queues_list(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing request queues."""
    result = await maybe_await(client.request_queues().list(limit=10))
    rq_page = cast('ListOfRequestQueues', result)

    assert rq_page is not None
    assert rq_page.items is not None
    assert isinstance(rq_page.items, list)


async def test_request_queues_list_pagination(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing request queues with pagination."""
    result = await maybe_await(client.request_queues().list(limit=5, offset=0))
    rq_page = cast('ListOfRequestQueues', result)

    assert rq_page is not None
    assert rq_page.items is not None
    assert isinstance(rq_page.items, list)


async def test_request_queues_get_or_create(client: ApifyClient | ApifyClientAsync) -> None:
    """Test get_or_create for request queues."""
    unique_name = f'test-rq-{uuid.uuid4().hex[:8]}'

    # Create new RQ
    result = await maybe_await(client.request_queues().get_or_create(name=unique_name))
    rq = cast('RequestQueue', result)
    assert rq is not None
    assert rq.name == unique_name

    # Get same RQ again (should return existing)
    result2 = await maybe_await(client.request_queues().get_or_create(name=unique_name))
    same_rq = cast('RequestQueue', result2)
    assert same_rq.id == rq.id

    # Cleanup
    await maybe_await(client.request_queue(rq.id).delete())
