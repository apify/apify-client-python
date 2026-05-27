"""Unified tests for request queue (sync + async)."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from datetime import timedelta
from typing import TYPE_CHECKING

from ._utils import get_random_resource_name, get_random_string, maybe_await, maybe_sleep
from apify_client._models import (
    BatchAddResult,
    BatchDeleteResult,
    ListOfRequestQueues,
    ListOfRequests,
    LockedRequestQueueHead,
    Request,
    RequestDraft,
    RequestLockInfo,
    RequestQueue,
    RequestQueueHead,
    RequestQueueShort,
    RequestRegistration,
    UnlockRequestsResult,
)

if TYPE_CHECKING:
    from apify_client import ApifyClient, ApifyClientAsync
    from apify_client._resource_clients.request_queue import RequestQueueClient, RequestQueueClientAsync
    from apify_client._typeddicts import (
        RequestDict,
        RequestDraftDeleteDict,
        RequestDraftDict,
    )


async def ensure_queue_is_populated(
    rq_client: RequestQueueClient | RequestQueueClientAsync,
    *,
    expected_count: int,
    is_async: bool,
) -> None:
    """Poll the queue until `expected_count` requests are visible.

    Uses `list_head` (without side effects) so polling does not lock items, which would otherwise
    lead to an ambiguous count of actually-locked requests in tests that exercise locking.
    """
    head_response: RequestQueueHead | None = None
    for _ in range(5):
        await maybe_sleep(1, is_async=is_async)
        result = await maybe_await(rq_client.list_head(limit=expected_count))
        assert isinstance(result, RequestQueueHead)
        head_response = result
        if len(head_response.items) == expected_count:
            break

    assert head_response is not None
    assert len(head_response.items) == expected_count


async def test_request_queue_collection_list(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing request queues."""
    rq_page = await maybe_await(client.request_queues().list(limit=10))
    assert isinstance(rq_page, ListOfRequestQueues)
    assert rq_page.items is not None
    assert isinstance(rq_page.items, list)


async def test_request_queue_collection_list_pagination(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing request queues with pagination."""
    rq_page = await maybe_await(client.request_queues().list(limit=5, offset=0))
    assert isinstance(rq_page, ListOfRequestQueues)
    assert rq_page.items is not None
    assert isinstance(rq_page.items, list)


async def test_request_queue_collection_get_or_create(client: ApifyClient | ApifyClientAsync) -> None:
    """Test get_or_create for request queues."""
    unique_name = get_random_resource_name('rq')

    # Create new RQ
    rq = await maybe_await(client.request_queues().get_or_create(name=unique_name))
    assert isinstance(rq, RequestQueue)

    try:
        assert rq.name == unique_name

        # Get same RQ again (should return existing)
        same_rq = await maybe_await(client.request_queues().get_or_create(name=unique_name))
        assert isinstance(same_rq, RequestQueue)
        assert same_rq.id == rq.id
    finally:
        await maybe_await(client.request_queue(rq.id).delete())


async def test_request_queue_lock(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    created_rq = await maybe_await(client.request_queues().get_or_create(name=get_random_resource_name('queue')))
    assert isinstance(created_rq, RequestQueue)
    rq = client.request_queue(created_rq.id, client_key=get_random_string(10))

    try:
        # Add requests and check if correct number of requests was locked
        for i in range(15):
            await maybe_await(
                rq.add_request({'url': f'http://test-lock.com/{i}', 'unique_key': f'http://test-lock.com/{i}'})
            )

        # Poll until all requests are available for locking (eventual consistency)
        get_head_and_lock_response: LockedRequestQueueHead | None = None
        for _ in range(5):
            await maybe_sleep(1, is_async=is_async)
            result = await maybe_await(rq.list_and_lock_head(limit=10, lock_duration=timedelta(seconds=10)))
            assert isinstance(result, LockedRequestQueueHead)
            get_head_and_lock_response = result
            if len(get_head_and_lock_response.items) == 10:
                break

        assert get_head_and_lock_response is not None
        assert len(get_head_and_lock_response.items) == 10

        for locked_request in get_head_and_lock_response.items:
            assert locked_request.lock_expires_at is not None

        # Check if the delete request works
        await maybe_await(rq.delete_request_lock(get_head_and_lock_response.items[1].id))

        """This is probably not working:
        delete_lock_request = await maybe_await(rq.get_request(get_head_and_lock_response.items[1].id))
        assert delete_lock_request is not None
        assert delete_lock_request.lock_expires_at is None
        """

        await maybe_await(rq.delete_request_lock(get_head_and_lock_response.items[2].id, forefront=True))

        """This is probably not working:
        delete_lock_request2 = await maybe_await(rq.get_request(get_head_and_lock_response.items[2].id))
        assert delete_lock_request2 is not None
        assert delete_lock_request2.lock_expires_at is None
        """

        # Check if the prolong request works
        prolong_request_lock_response = await maybe_await(
            rq.prolong_request_lock(
                get_head_and_lock_response.items[3].id,
                lock_duration=timedelta(seconds=15),
            )
        )
        assert isinstance(prolong_request_lock_response, RequestLockInfo)
        assert prolong_request_lock_response.lock_expires_at is not None
    finally:
        await maybe_await(rq.delete())


async def test_request_queue_get_or_create_and_get(client: ApifyClient | ApifyClientAsync) -> None:
    """Test creating a request queue and retrieving it."""
    rq_name = get_random_resource_name('queue')

    # Create queue
    created_rq = await maybe_await(client.request_queues().get_or_create(name=rq_name))
    assert isinstance(created_rq, RequestQueue)
    rq_client = client.request_queue(created_rq.id)

    try:
        assert created_rq.id is not None
        assert created_rq.name == rq_name

        # Get the same queue
        retrieved_rq = await maybe_await(rq_client.get())
        assert isinstance(retrieved_rq, RequestQueue)
        assert retrieved_rq.id == created_rq.id
        assert retrieved_rq.name == rq_name
    finally:
        await maybe_await(rq_client.delete())


async def test_request_queue_update(client: ApifyClient | ApifyClientAsync) -> None:
    """Test updating request queue properties."""
    rq_name = get_random_resource_name('queue')
    new_name = get_random_resource_name('queue-updated')

    created_rq = await maybe_await(client.request_queues().get_or_create(name=rq_name))
    assert isinstance(created_rq, RequestQueue)
    rq_client = client.request_queue(created_rq.id)

    try:
        # Update the name
        updated_rq = await maybe_await(rq_client.update(name=new_name))
        assert isinstance(updated_rq, RequestQueue)
        assert updated_rq.name == new_name
        assert updated_rq.id == created_rq.id

        # Verify the update persisted
        retrieved_rq = await maybe_await(rq_client.get())
        assert isinstance(retrieved_rq, RequestQueue)
        assert retrieved_rq.name == new_name
    finally:
        await maybe_await(rq_client.delete())


async def test_request_queue_add_and_get_request(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test adding and getting a request from the queue."""
    rq_name = get_random_resource_name('queue')

    created_rq = await maybe_await(client.request_queues().get_or_create(name=rq_name))
    assert isinstance(created_rq, RequestQueue)
    rq_client = client.request_queue(created_rq.id)

    try:
        # Add a request
        request_data: RequestDraftDict = {
            'url': 'https://example.com/test',
            'unique_key': 'test-key-1',
            'method': 'GET',
        }
        add_result = await maybe_await(rq_client.add_request(request_data))
        assert isinstance(add_result, RequestRegistration)
        assert add_result.request_id is not None
        assert add_result.was_already_present is False

        # Wait briefly for eventual consistency
        await maybe_sleep(1, is_async=is_async)

        # Get the request
        request = await maybe_await(rq_client.get_request(add_result.request_id))
        assert isinstance(request, Request)
        assert str(request.url) == 'https://example.com/test'
        assert request.unique_key == 'test-key-1'
    finally:
        await maybe_await(rq_client.delete())


async def test_request_queue_list_head(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test listing requests from the head of the queue."""
    rq_name = get_random_resource_name('queue')

    created_rq = await maybe_await(client.request_queues().get_or_create(name=rq_name))
    assert isinstance(created_rq, RequestQueue)
    rq_client = client.request_queue(created_rq.id)

    try:
        # Add multiple requests
        for i in range(5):
            await maybe_await(
                rq_client.add_request({'url': f'https://example.com/page-{i}', 'unique_key': f'page-{i}'})
            )

        # Poll until requests are available (eventual consistency)
        head_response: RequestQueueHead | None = None
        for _ in range(5):
            await maybe_sleep(1, is_async=is_async)
            result = await maybe_await(rq_client.list_head(limit=3))
            assert isinstance(result, RequestQueueHead)
            head_response = result
            if len(head_response.items) == 3:
                break

        assert head_response is not None
        assert len(head_response.items) == 3
    finally:
        await maybe_await(rq_client.delete())


async def test_request_queue_list_requests(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test listing all requests in the queue."""
    rq_name = get_random_resource_name('queue')

    created_rq = await maybe_await(client.request_queues().get_or_create(name=rq_name))
    assert isinstance(created_rq, RequestQueue)
    rq_client = client.request_queue(created_rq.id)

    try:
        # Add multiple requests
        for i in range(5):
            await maybe_await(
                rq_client.add_request({'url': f'https://example.com/item-{i}', 'unique_key': f'item-{i}'})
            )

        # Poll until all requests are available (eventual consistency)
        list_response: ListOfRequests | None = None
        for _ in range(5):
            await maybe_sleep(1, is_async=is_async)
            result = await maybe_await(rq_client.list_requests())
            assert isinstance(result, ListOfRequests)
            list_response = result
            if len(list_response.items) == 5:
                break

        assert list_response is not None
        assert len(list_response.items) == 5
    finally:
        await maybe_await(rq_client.delete())


async def test_request_queue_delete_request(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test deleting a request from the queue."""
    rq_name = get_random_resource_name('queue')

    created_rq = await maybe_await(client.request_queues().get_or_create(name=rq_name))
    assert isinstance(created_rq, RequestQueue)
    rq_client = client.request_queue(created_rq.id)

    try:
        # Add a request
        add_result = await maybe_await(
            rq_client.add_request({'url': 'https://example.com/to-delete', 'unique_key': 'delete-me'})
        )
        assert isinstance(add_result, RequestRegistration)

        # Wait briefly for eventual consistency
        await maybe_sleep(1, is_async=is_async)

        # Verify it exists
        request = await maybe_await(rq_client.get_request(add_result.request_id))
        assert request is not None

        # Delete the request
        await maybe_await(rq_client.delete_request(add_result.request_id))

        # Wait briefly
        await maybe_sleep(1, is_async=is_async)

        # Verify it's gone
        deleted_request = await maybe_await(rq_client.get_request(add_result.request_id))
        assert deleted_request is None
    finally:
        await maybe_await(rq_client.delete())


async def test_request_queue_batch_add_requests(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test adding multiple requests in batch."""
    rq_name = get_random_resource_name('queue')

    created_rq = await maybe_await(client.request_queues().get_or_create(name=rq_name))
    assert isinstance(created_rq, RequestQueue)
    rq_client = client.request_queue(created_rq.id)

    try:
        # Batch add requests
        requests_to_add: list[RequestDraftDict] = [
            {'url': f'https://example.com/batch-{i}', 'unique_key': f'batch-{i}'} for i in range(10)
        ]
        batch_response = await maybe_await(rq_client.batch_add_requests(requests_to_add))
        assert isinstance(batch_response, BatchAddResult)
        assert len(batch_response.processed_requests) == 10
        assert len(batch_response.unprocessed_requests) == 0

        # Poll until all requests are available (eventual consistency)
        list_response: ListOfRequests | None = None
        for _ in range(5):
            await maybe_sleep(1, is_async=is_async)
            result = await maybe_await(rq_client.list_requests())
            assert isinstance(result, ListOfRequests)
            list_response = result
            if len(list_response.items) == 10:
                break

        assert list_response is not None
        assert len(list_response.items) == 10
    finally:
        await maybe_await(rq_client.delete())


async def test_request_queue_batch_delete_requests(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test deleting multiple requests in batch."""
    rq_name = get_random_resource_name('queue')

    created_rq = await maybe_await(client.request_queues().get_or_create(name=rq_name))
    assert isinstance(created_rq, RequestQueue)
    rq_client = client.request_queue(created_rq.id)

    try:
        # Add requests
        for i in range(10):
            await maybe_await(
                rq_client.add_request({'url': f'https://example.com/delete-{i}', 'unique_key': f'delete-{i}'})
            )

        # Poll until all requests are available (eventual consistency)
        list_response: ListOfRequests | None = None
        for _ in range(5):
            await maybe_sleep(1, is_async=is_async)
            result = await maybe_await(rq_client.list_requests())
            assert isinstance(result, ListOfRequests)
            list_response = result
            if len(list_response.items) == 10:
                break

        assert list_response is not None
        assert len(list_response.items) == 10
        requests_to_delete: list[RequestDraftDeleteDict] = []
        for item in list_response.items[:5]:
            assert item.unique_key is not None
            requests_to_delete.append({'unique_key': item.unique_key})

        # Batch delete
        delete_response = await maybe_await(rq_client.batch_delete_requests(requests_to_delete))
        assert isinstance(delete_response, BatchDeleteResult)
        assert len(delete_response.processed_requests) == 5

        # Poll until deletions are reflected (eventual consistency)
        remaining: ListOfRequests | None = None
        for _ in range(5):
            await maybe_sleep(1, is_async=is_async)
            result = await maybe_await(rq_client.list_requests())
            assert isinstance(result, ListOfRequests)
            remaining = result
            if len(remaining.items) == 5:
                break

        assert remaining is not None
        assert len(remaining.items) == 5
    finally:
        await maybe_await(rq_client.delete())


async def test_request_queue_delete_nonexistent(client: ApifyClient | ApifyClientAsync) -> None:
    """Test that getting a deleted queue returns None."""
    rq_name = get_random_resource_name('queue')

    created_rq = await maybe_await(client.request_queues().get_or_create(name=rq_name))
    assert isinstance(created_rq, RequestQueue)
    rq_client = client.request_queue(created_rq.id)

    # Delete queue
    await maybe_await(rq_client.delete())

    # Verify it's gone
    retrieved_rq = await maybe_await(rq_client.get())
    assert retrieved_rq is None


async def test_request_queue_list_and_lock_head(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test locking requests from the head of the queue."""
    rq_name = get_random_resource_name('queue')

    created_rq = await maybe_await(client.request_queues().get_or_create(name=rq_name))
    assert isinstance(created_rq, RequestQueue)
    rq_client = client.request_queue(created_rq.id, client_key=get_random_string(10))

    try:
        # Add multiple requests
        for i in range(5):
            await maybe_await(
                rq_client.add_request({'url': f'https://example.com/lock-{i}', 'unique_key': f'lock-{i}'})
            )

        await ensure_queue_is_populated(rq_client, expected_count=5, is_async=is_async)

        result = await maybe_await(rq_client.list_and_lock_head(limit=3, lock_duration=timedelta(seconds=60)))
        assert isinstance(result, LockedRequestQueueHead)
        lock_response = result
        assert len(lock_response.items) == 3

        # Verify requests are locked
        for locked_request in lock_response.items:
            assert locked_request.id is not None
            assert locked_request.lock_expires_at is not None
    finally:
        await maybe_await(rq_client.delete())


async def test_request_queue_prolong_request_lock(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test prolonging a request lock."""
    rq_name = get_random_resource_name('queue')

    created_rq = await maybe_await(client.request_queues().get_or_create(name=rq_name))
    assert isinstance(created_rq, RequestQueue)
    rq_client = client.request_queue(created_rq.id, client_key=get_random_string(10))

    try:
        # Add a request
        await maybe_await(rq_client.add_request({'url': 'https://example.com/prolong', 'unique_key': 'prolong-test'}))

        # Poll until the request is available for locking (eventual consistency)
        lock_response: LockedRequestQueueHead | None = None
        for _ in range(5):
            await maybe_sleep(1, is_async=is_async)
            result = await maybe_await(rq_client.list_and_lock_head(limit=1, lock_duration=timedelta(seconds=60)))
            assert isinstance(result, LockedRequestQueueHead)
            lock_response = result
            if len(lock_response.items) == 1:
                break

        assert lock_response is not None
        assert len(lock_response.items) == 1
        locked_request = lock_response.items[0]
        original_lock_expires = locked_request.lock_expires_at

        # Prolong the lock
        prolong_response = await maybe_await(
            rq_client.prolong_request_lock(locked_request.id, lock_duration=timedelta(seconds=120))
        )
        assert isinstance(prolong_response, RequestLockInfo)
        assert prolong_response.lock_expires_at is not None
        assert prolong_response.lock_expires_at > original_lock_expires
    finally:
        await maybe_await(rq_client.delete())


async def test_request_queue_delete_request_lock(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test deleting a request lock."""
    rq_name = get_random_resource_name('queue')

    created_rq = await maybe_await(client.request_queues().get_or_create(name=rq_name))
    assert isinstance(created_rq, RequestQueue)
    rq_client = client.request_queue(created_rq.id, client_key=get_random_string(10))

    try:
        # Add a request
        await maybe_await(rq_client.add_request({'url': 'https://example.com/unlock', 'unique_key': 'unlock-test'}))

        # Poll until the request is available for locking (eventual consistency)
        lock_response: LockedRequestQueueHead | None = None
        for _ in range(5):
            await maybe_sleep(1, is_async=is_async)
            result = await maybe_await(rq_client.list_and_lock_head(limit=1, lock_duration=timedelta(seconds=60)))
            assert isinstance(result, LockedRequestQueueHead)
            lock_response = result
            if len(lock_response.items) == 1:
                break

        assert lock_response is not None
        assert len(lock_response.items) == 1
        locked_request = lock_response.items[0]

        # Delete the lock
        await maybe_await(rq_client.delete_request_lock(locked_request.id))

        # Verify the operation succeeded (no exception thrown)
        # The request should still exist but be unlocked
        request = await maybe_await(rq_client.get_request(locked_request.id))
        assert request is not None
    finally:
        await maybe_await(rq_client.delete())


async def test_request_queue_unlock_requests(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test unlocking all requests locked by the client."""
    rq_name = get_random_resource_name('queue')

    created_rq = await maybe_await(client.request_queues().get_or_create(name=rq_name))
    assert isinstance(created_rq, RequestQueue)
    rq_client = client.request_queue(created_rq.id, client_key=get_random_string(10))

    try:
        # Add multiple requests
        for i in range(5):
            await maybe_await(
                rq_client.add_request({'url': f'https://example.com/unlock-{i}', 'unique_key': f'unlock-{i}'})
            )

        await ensure_queue_is_populated(rq_client, expected_count=5, is_async=is_async)

        result = await maybe_await(rq_client.list_and_lock_head(limit=3, lock_duration=timedelta(seconds=60)))
        assert isinstance(result, LockedRequestQueueHead)
        lock_response = result
        assert len(lock_response.items) == 3

        # Unlock all requests
        unlock_response = await maybe_await(rq_client.unlock_requests())
        assert isinstance(unlock_response, UnlockRequestsResult)
        assert unlock_response.unlocked_count == 3
    finally:
        await maybe_await(rq_client.delete())


async def test_request_queue_update_request(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test updating a request in the queue."""
    rq_name = get_random_resource_name('queue')

    created_rq = await maybe_await(client.request_queues().get_or_create(name=rq_name))
    assert isinstance(created_rq, RequestQueue)
    rq_client = client.request_queue(created_rq.id)

    try:
        # Add a request
        request_data: RequestDraftDict = {
            'url': 'https://example.com/original',
            'unique_key': 'update-test',
            'method': 'GET',
        }
        add_result = await maybe_await(rq_client.add_request(request_data))
        assert isinstance(add_result, RequestRegistration)
        assert add_result.request_id is not None

        # Wait briefly for eventual consistency
        await maybe_sleep(1, is_async=is_async)

        # Get the request to get its full data
        original_request = await maybe_await(rq_client.get_request(add_result.request_id))
        assert isinstance(original_request, Request)

        assert original_request.unique_key is not None
        # Update the request (change method and add user data)
        updated_request_data: RequestDict = {
            'id': add_result.request_id,
            'url': str(original_request.url),
            'unique_key': original_request.unique_key,
            'method': 'POST',
            'user_data': {'updated': True},
        }
        update_result = await maybe_await(rq_client.update_request(updated_request_data))
        assert isinstance(update_result, RequestRegistration)
        assert update_result.request_id == add_result.request_id
    finally:
        await maybe_await(rq_client.delete())


async def test_request_queue_collection_iterate(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test paginated iteration over user request queues."""
    created_ids: list[str] = []

    for _ in range(3):
        rq = await maybe_await(client.request_queues().get_or_create(name=get_random_resource_name('rq')))
        assert isinstance(rq, RequestQueue)
        created_ids.append(rq.id)

    try:
        iterator = client.request_queues().iterate(desc=True)
        collected: list[RequestQueueShort] = []
        if is_async:
            assert isinstance(iterator, AsyncIterator)
            async for rq in iterator:
                assert isinstance(rq, RequestQueueShort)
                collected.append(rq)
        else:
            assert isinstance(iterator, Iterator)
            for rq in iterator:
                assert isinstance(rq, RequestQueueShort)
                collected.append(rq)

        collected_ids = {rq.id for rq in collected}
        for rq_id in created_ids:
            assert rq_id in collected_ids
    finally:
        for rq_id in created_ids:
            await maybe_await(client.request_queue(rq_id).delete())


async def test_request_queue_iterate_requests(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test paginated iteration over requests within a queue."""
    rq = await maybe_await(client.request_queues().get_or_create(name=get_random_resource_name('rq')))
    assert isinstance(rq, RequestQueue)
    rq_client = client.request_queue(rq.id)

    try:
        # Add several requests
        added_urls: list[str] = []
        for i in range(7):
            request_draft = RequestDraft(url=f'https://example.com/page-{i}', unique_key=f'unique-{i}')
            await maybe_await(rq_client.add_request(request_draft))
            added_urls.append(request_draft.url)

        # Wait until all 7 requests are indexed (eventual consistency)
        await ensure_queue_is_populated(rq_client, expected_count=7, is_async=is_async)

        # Iterate with a small chunk so multiple pages are fetched
        iterator = rq_client.iterate_requests(chunk_size=3)
        collected: list[Request] = []
        if is_async:
            assert isinstance(iterator, AsyncIterator)
            async for req in iterator:
                assert isinstance(req, Request)
                collected.append(req)
        else:
            assert isinstance(iterator, Iterator)
            for req in iterator:
                assert isinstance(req, Request)
                collected.append(req)

        assert len(collected) == 7
        collected_urls = {r.url for r in collected if r.url is not None}
        for url in added_urls:
            assert url in collected_urls
    finally:
        await maybe_await(rq_client.delete())


async def test_request_queue_list_requests_with_cursor(
    client: ApifyClient | ApifyClientAsync, *, is_async: bool
) -> None:
    """Test list_requests pagination via limit and the opaque cursor token."""
    rq = await maybe_await(client.request_queues().get_or_create(name=get_random_resource_name('rq')))
    assert isinstance(rq, RequestQueue)
    rq_client = client.request_queue(rq.id)

    try:
        for i in range(5):
            await maybe_await(
                rq_client.add_request(RequestDraft(url=f'https://example.com/p-{i}', unique_key=f'u-{i}'))
            )

        # Wait for all 5 requests to be indexed so pagination is exercised, not truncated
        await ensure_queue_is_populated(rq_client, expected_count=5, is_async=is_async)

        # First page
        first_page = await maybe_await(rq_client.list_requests(limit=2))
        assert isinstance(first_page, ListOfRequests)
        assert len(first_page.items) == 2

        # The API must return a continuation token when more pages exist (5 items, limit=2)
        assert first_page.next_cursor is not None
        second_page = await maybe_await(rq_client.list_requests(limit=10, cursor=first_page.next_cursor))
        assert isinstance(second_page, ListOfRequests)

        first_ids = {r.id for r in first_page.items}
        second_ids = {r.id for r in second_page.items}
        assert first_ids.isdisjoint(second_ids)
    finally:
        await maybe_await(rq_client.delete())


async def test_request_queue_list_requests_with_filter(
    client: ApifyClient | ApifyClientAsync, *, is_async: bool
) -> None:
    """Test list_requests with the `filter` parameter (pending only)."""
    rq = await maybe_await(client.request_queues().get_or_create(name=get_random_resource_name('rq')))
    assert isinstance(rq, RequestQueue)
    rq_client = client.request_queue(rq.id)

    try:
        for i in range(3):
            await maybe_await(
                rq_client.add_request(RequestDraft(url=f'https://example.com/f-{i}', unique_key=f'f-{i}'))
            )

        # Wait for all 3 requests to be indexed before filtering
        await ensure_queue_is_populated(rq_client, expected_count=3, is_async=is_async)

        # All three requests are pending - filter=['pending'] should return all of them.
        pending_page = await maybe_await(rq_client.list_requests(filter=['pending']))
        assert isinstance(pending_page, ListOfRequests)
        assert len(pending_page.items) == 3
    finally:
        await maybe_await(rq_client.delete())
