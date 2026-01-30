"""Unified tests for request queue (sync + async)."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from apify_client import ApifyClient, ApifyClientAsync
    from apify_client._models import (
        BatchAddResult,
        BatchDeleteResult,
        ListOfRequestQueues,
        ListOfRequests,
        LockedRequestQueueHead,
        Request,
        RequestLockInfo,
        RequestQueue,
        RequestQueueHead,
        RequestRegistration,
        UnlockRequestsResult,
    )


from datetime import timedelta

from .conftest import get_random_resource_name, get_random_string, maybe_await, maybe_sleep


async def test_request_queue_collection_list(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing request queues."""
    result = await maybe_await(client.request_queues().list(limit=10))
    rq_page = cast('ListOfRequestQueues', result)

    assert rq_page is not None
    assert rq_page.items is not None
    assert isinstance(rq_page.items, list)


async def test_request_queue_collection_list_pagination(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing request queues with pagination."""
    result = await maybe_await(client.request_queues().list(limit=5, offset=0))
    rq_page = cast('ListOfRequestQueues', result)

    assert rq_page is not None
    assert rq_page.items is not None
    assert isinstance(rq_page.items, list)


async def test_request_queue_collection_get_or_create(client: ApifyClient | ApifyClientAsync) -> None:
    """Test get_or_create for request queues."""
    unique_name = get_random_resource_name('rq')

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


async def test_request_queue_lock(client: ApifyClient | ApifyClientAsync) -> None:
    result = await maybe_await(client.request_queues().get_or_create(name=get_random_resource_name('queue')))
    created_rq = cast('RequestQueue', result)
    rq = client.request_queue(created_rq.id, client_key=get_random_string(10))

    # Add requests and check if correct number of requests was locked
    for i in range(15):
        await maybe_await(
            rq.add_request({'url': f'http://test-lock.com/{i}', 'uniqueKey': f'http://test-lock.com/{i}'})
        )

    result = await maybe_await(rq.list_and_lock_head(limit=10, lock_duration=timedelta(seconds=10)))
    get_head_and_lock_response = cast('LockedRequestQueueHead', result)

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
    result = await maybe_await(
        rq.prolong_request_lock(
            get_head_and_lock_response.items[3].id,
            lock_duration=timedelta(seconds=15),
        )
    )
    prolong_request_lock_response = cast('RequestLockInfo', result)
    assert prolong_request_lock_response is not None
    assert prolong_request_lock_response.lock_expires_at is not None

    await maybe_await(rq.delete())
    result = await maybe_await(client.request_queue(created_rq.id).get())
    assert result is None


async def test_request_queue_get_or_create_and_get(client: ApifyClient | ApifyClientAsync) -> None:
    """Test creating a request queue and retrieving it."""
    rq_name = get_random_resource_name('queue')

    # Create queue
    result = await maybe_await(client.request_queues().get_or_create(name=rq_name))
    created_rq = cast('RequestQueue', result)
    assert created_rq is not None
    assert created_rq.id is not None
    assert created_rq.name == rq_name

    # Get the same queue
    rq_client = client.request_queue(created_rq.id)
    result = await maybe_await(rq_client.get())
    retrieved_rq = cast('RequestQueue', result)
    assert retrieved_rq is not None
    assert retrieved_rq.id == created_rq.id
    assert retrieved_rq.name == rq_name

    # Cleanup
    await maybe_await(rq_client.delete())


async def test_request_queue_update(client: ApifyClient | ApifyClientAsync) -> None:
    """Test updating request queue properties."""
    rq_name = get_random_resource_name('queue')
    new_name = get_random_resource_name('queue-updated')

    result = await maybe_await(client.request_queues().get_or_create(name=rq_name))
    created_rq = cast('RequestQueue', result)
    rq_client = client.request_queue(created_rq.id)

    # Update the name
    result = await maybe_await(rq_client.update(name=new_name))
    updated_rq = cast('RequestQueue', result)
    assert updated_rq is not None
    assert updated_rq.name == new_name
    assert updated_rq.id == created_rq.id

    # Verify the update persisted
    result = await maybe_await(rq_client.get())
    retrieved_rq = cast('RequestQueue', result)
    assert retrieved_rq is not None
    assert retrieved_rq.name == new_name

    # Cleanup
    await maybe_await(rq_client.delete())


async def test_request_queue_add_and_get_request(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test adding and getting a request from the queue."""
    rq_name = get_random_resource_name('queue')

    result = await maybe_await(client.request_queues().get_or_create(name=rq_name))
    created_rq = cast('RequestQueue', result)
    rq_client = client.request_queue(created_rq.id)

    # Add a request
    request_data = {
        'url': 'https://example.com/test',
        'uniqueKey': 'test-key-1',
        'method': 'GET',
    }
    result = await maybe_await(rq_client.add_request(request_data))
    add_result = cast('RequestRegistration', result)
    assert add_result is not None
    assert add_result.request_id is not None
    assert add_result.was_already_present is False

    # Wait briefly for eventual consistency
    await maybe_sleep(1, is_async=is_async)

    # Get the request
    result = await maybe_await(rq_client.get_request(add_result.request_id))
    request = cast('Request', result)
    assert request is not None
    assert str(request.url) == 'https://example.com/test'
    assert request.unique_key == 'test-key-1'

    # Cleanup
    await maybe_await(rq_client.delete())


async def test_request_queue_list_head(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test listing requests from the head of the queue."""
    rq_name = get_random_resource_name('queue')

    result = await maybe_await(client.request_queues().get_or_create(name=rq_name))
    created_rq = cast('RequestQueue', result)
    rq_client = client.request_queue(created_rq.id)

    # Add multiple requests
    for i in range(5):
        await maybe_await(
            rq_client.add_request(
                {
                    'url': f'https://example.com/page-{i}',
                    'uniqueKey': f'page-{i}',
                }
            )
        )

    # Wait briefly for eventual consistency
    await maybe_sleep(1, is_async=is_async)

    # List head
    result = await maybe_await(rq_client.list_head(limit=3))
    head_response = cast('RequestQueueHead', result)
    assert head_response is not None
    assert len(head_response.items) == 3

    # Cleanup
    await maybe_await(rq_client.delete())


async def test_request_queue_list_requests(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test listing all requests in the queue."""
    rq_name = get_random_resource_name('queue')

    result = await maybe_await(client.request_queues().get_or_create(name=rq_name))
    created_rq = cast('RequestQueue', result)
    rq_client = client.request_queue(created_rq.id)

    # Add multiple requests
    for i in range(5):
        await maybe_await(
            rq_client.add_request(
                {
                    'url': f'https://example.com/item-{i}',
                    'uniqueKey': f'item-{i}',
                }
            )
        )

    # Wait briefly for eventual consistency
    await maybe_sleep(1, is_async=is_async)

    # List all requests
    result = await maybe_await(rq_client.list_requests())
    list_response = cast('ListOfRequests', result)
    assert list_response is not None
    assert len(list_response.items) == 5

    # Cleanup
    await maybe_await(rq_client.delete())


async def test_request_queue_delete_request(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test deleting a request from the queue."""
    rq_name = get_random_resource_name('queue')

    result = await maybe_await(client.request_queues().get_or_create(name=rq_name))
    created_rq = cast('RequestQueue', result)
    rq_client = client.request_queue(created_rq.id)

    # Add a request
    result = await maybe_await(
        rq_client.add_request(
            {
                'url': 'https://example.com/to-delete',
                'uniqueKey': 'delete-me',
            }
        )
    )
    add_result = cast('RequestRegistration', result)

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

    # Cleanup
    await maybe_await(rq_client.delete())


async def test_request_queue_batch_add_requests(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test adding multiple requests in batch."""
    rq_name = get_random_resource_name('queue')

    result = await maybe_await(client.request_queues().get_or_create(name=rq_name))
    created_rq = cast('RequestQueue', result)
    rq_client = client.request_queue(created_rq.id)

    # Batch add requests
    requests_to_add = [{'url': f'https://example.com/batch-{i}', 'uniqueKey': f'batch-{i}'} for i in range(10)]
    result = await maybe_await(rq_client.batch_add_requests(requests_to_add))
    batch_response = cast('BatchAddResult', result)
    assert batch_response is not None
    assert len(batch_response.processed_requests) == 10
    assert len(batch_response.unprocessed_requests) == 0

    # Wait briefly for eventual consistency
    await maybe_sleep(1, is_async=is_async)

    # Verify requests were added
    result = await maybe_await(rq_client.list_requests())
    list_response = cast('ListOfRequests', result)
    assert len(list_response.items) == 10

    # Cleanup
    await maybe_await(rq_client.delete())


async def test_request_queue_batch_delete_requests(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test deleting multiple requests in batch."""
    rq_name = get_random_resource_name('queue')

    result = await maybe_await(client.request_queues().get_or_create(name=rq_name))
    created_rq = cast('RequestQueue', result)
    rq_client = client.request_queue(created_rq.id)

    # Add requests
    for i in range(10):
        await maybe_await(
            rq_client.add_request(
                {
                    'url': f'https://example.com/delete-{i}',
                    'uniqueKey': f'delete-{i}',
                }
            )
        )

    # Wait briefly for eventual consistency
    await maybe_sleep(1, is_async=is_async)

    # List requests to get IDs
    result = await maybe_await(rq_client.list_requests())
    list_response = cast('ListOfRequests', result)
    requests_to_delete = [{'uniqueKey': item.unique_key} for item in list_response.items[:5]]

    # Batch delete
    result = await maybe_await(rq_client.batch_delete_requests(requests_to_delete))
    delete_response = cast('BatchDeleteResult', result)
    assert delete_response is not None
    assert len(delete_response.processed_requests) == 5

    # Wait briefly
    await maybe_sleep(1, is_async=is_async)

    # Verify remaining requests
    result = await maybe_await(rq_client.list_requests())
    remaining = cast('ListOfRequests', result)
    assert len(remaining.items) == 5

    # Cleanup
    await maybe_await(rq_client.delete())


async def test_request_queue_delete_nonexistent(client: ApifyClient | ApifyClientAsync) -> None:
    """Test that getting a deleted queue returns None."""
    rq_name = get_random_resource_name('queue')

    result = await maybe_await(client.request_queues().get_or_create(name=rq_name))
    created_rq = cast('RequestQueue', result)
    rq_client = client.request_queue(created_rq.id)

    # Delete queue
    await maybe_await(rq_client.delete())

    # Verify it's gone
    retrieved_rq = await maybe_await(rq_client.get())
    assert retrieved_rq is None


async def test_request_queue_list_and_lock_head(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test locking requests from the head of the queue."""
    rq_name = get_random_resource_name('queue')

    result = await maybe_await(client.request_queues().get_or_create(name=rq_name))
    created_rq = cast('RequestQueue', result)
    rq_client = client.request_queue(created_rq.id, client_key=get_random_string(10))

    # Add multiple requests
    for i in range(5):
        await maybe_await(rq_client.add_request({'url': f'https://example.com/lock-{i}', 'uniqueKey': f'lock-{i}'}))

    # Wait briefly for eventual consistency
    await maybe_sleep(1, is_async=is_async)

    # Lock head requests
    result = await maybe_await(rq_client.list_and_lock_head(limit=3, lock_duration=timedelta(seconds=60)))
    lock_response = cast('LockedRequestQueueHead', result)
    assert lock_response is not None
    assert len(lock_response.items) == 3

    # Verify requests are locked
    for locked_request in lock_response.items:
        assert locked_request.id is not None
        assert locked_request.lock_expires_at is not None

    # Cleanup
    await maybe_await(rq_client.delete())


async def test_request_queue_prolong_request_lock(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test prolonging a request lock."""
    rq_name = get_random_resource_name('queue')

    result = await maybe_await(client.request_queues().get_or_create(name=rq_name))
    created_rq = cast('RequestQueue', result)
    rq_client = client.request_queue(created_rq.id, client_key=get_random_string(10))

    # Add a request
    await maybe_await(rq_client.add_request({'url': 'https://example.com/prolong', 'uniqueKey': 'prolong-test'}))

    # Wait briefly for eventual consistency
    await maybe_sleep(1, is_async=is_async)

    # Lock the request
    result = await maybe_await(rq_client.list_and_lock_head(limit=1, lock_duration=timedelta(seconds=60)))
    lock_response = cast('LockedRequestQueueHead', result)
    assert len(lock_response.items) == 1
    locked_request = lock_response.items[0]
    original_lock_expires = locked_request.lock_expires_at

    # Prolong the lock
    result = await maybe_await(rq_client.prolong_request_lock(locked_request.id, lock_duration=timedelta(seconds=120)))
    prolong_response = cast('RequestLockInfo', result)
    assert prolong_response is not None
    assert prolong_response.lock_expires_at is not None
    assert prolong_response.lock_expires_at > original_lock_expires

    # Cleanup
    await maybe_await(rq_client.delete())


async def test_request_queue_delete_request_lock(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test deleting a request lock."""
    rq_name = get_random_resource_name('queue')

    result = await maybe_await(client.request_queues().get_or_create(name=rq_name))
    created_rq = cast('RequestQueue', result)
    rq_client = client.request_queue(created_rq.id, client_key=get_random_string(10))

    # Add a request
    await maybe_await(rq_client.add_request({'url': 'https://example.com/unlock', 'uniqueKey': 'unlock-test'}))

    # Wait briefly for eventual consistency
    await maybe_sleep(1, is_async=is_async)

    # Lock the request
    result = await maybe_await(rq_client.list_and_lock_head(limit=1, lock_duration=timedelta(seconds=60)))
    lock_response = cast('LockedRequestQueueHead', result)
    assert len(lock_response.items) == 1
    locked_request = lock_response.items[0]

    # Delete the lock
    await maybe_await(rq_client.delete_request_lock(locked_request.id))

    # Verify the operation succeeded (no exception thrown)
    # The request should still exist but be unlocked
    request = await maybe_await(rq_client.get_request(locked_request.id))
    assert request is not None

    # Cleanup
    await maybe_await(rq_client.delete())


async def test_request_queue_unlock_requests(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test unlocking all requests locked by the client."""
    rq_name = get_random_resource_name('queue')

    result = await maybe_await(client.request_queues().get_or_create(name=rq_name))
    created_rq = cast('RequestQueue', result)
    rq_client = client.request_queue(created_rq.id, client_key=get_random_string(10))

    # Add multiple requests
    for i in range(5):
        await maybe_await(rq_client.add_request({'url': f'https://example.com/unlock-{i}', 'uniqueKey': f'unlock-{i}'}))

    # Wait briefly for eventual consistency
    await maybe_sleep(1, is_async=is_async)

    # Lock some requests
    result = await maybe_await(rq_client.list_and_lock_head(limit=3, lock_duration=timedelta(seconds=60)))
    lock_response = cast('LockedRequestQueueHead', result)
    assert len(lock_response.items) == 3

    # Unlock all requests
    result = await maybe_await(rq_client.unlock_requests())
    unlock_response = cast('UnlockRequestsResult', result)
    assert unlock_response is not None
    assert unlock_response.unlocked_count == 3

    # Cleanup
    await maybe_await(rq_client.delete())


async def test_request_queue_update_request(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test updating a request in the queue."""
    rq_name = get_random_resource_name('queue')

    result = await maybe_await(client.request_queues().get_or_create(name=rq_name))
    created_rq = cast('RequestQueue', result)
    rq_client = client.request_queue(created_rq.id)

    # Add a request
    request_data = {
        'url': 'https://example.com/original',
        'uniqueKey': 'update-test',
        'method': 'GET',
    }
    result = await maybe_await(rq_client.add_request(request_data))
    add_result = cast('RequestRegistration', result)
    assert add_result is not None
    assert add_result.request_id is not None

    # Wait briefly for eventual consistency
    await maybe_sleep(1, is_async=is_async)

    # Get the request to get its full data
    result = await maybe_await(rq_client.get_request(add_result.request_id))
    original_request = cast('Request', result)
    assert original_request is not None

    # Update the request (change method and add user data)
    updated_request_data = {
        'id': add_result.request_id,
        'url': str(original_request.url),
        'uniqueKey': original_request.unique_key,
        'method': 'POST',
        'userData': {'updated': True},
    }
    result = await maybe_await(rq_client.update_request(updated_request_data))
    update_result = cast('RequestRegistration', result)
    assert update_result is not None
    assert update_result.request_id == add_result.request_id

    # Cleanup
    await maybe_await(rq_client.delete())
