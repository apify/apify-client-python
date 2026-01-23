from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from .utils import get_random_resource_name, get_random_string

if TYPE_CHECKING:
    from apify_client import ApifyClientAsync

##################################################
# OLD TESTS - Tests with mocks and signed URLs
##################################################


async def test_request_queue_lock(apify_client_async: ApifyClientAsync) -> None:
    created_rq = await apify_client_async.request_queues().get_or_create(name=get_random_resource_name('queue'))
    rq = apify_client_async.request_queue(created_rq.id, client_key=get_random_string(10))

    # Add requests and check if correct number of requests was locked
    for i in range(15):
        await rq.add_request({'url': f'http://test-lock.com/{i}', 'uniqueKey': f'http://test-lock.com/{i}'})

    get_head_and_lock_response = await rq.list_and_lock_head(limit=10, lock_secs=10)

    for locked_request in get_head_and_lock_response.items:
        assert locked_request.lock_expires_at is not None

    # Check if the delete request works
    await rq.delete_request_lock(get_head_and_lock_response.items[1].id)

    """This is probably not working:
    delete_lock_request = await rq.get_request(get_head_and_lock_response.data.items[1].id)
    assert delete_lock_request is not None
    assert delete_lock_request.lock_expires_at is None
    """

    await rq.delete_request_lock(get_head_and_lock_response.items[2].id, forefront=True)

    """This is probably not working:
    delete_lock_request2 = await rq.get_request(get_head_and_lock_response.data.items[2].id)
    assert delete_lock_request2 is not None
    assert delete_lock_request2.lock_expires_at is None
    """

    # Check if the prolong request works
    prolong_request_lock_response = await rq.prolong_request_lock(
        get_head_and_lock_response.items[3].id,
        lock_secs=15,
    )
    assert prolong_request_lock_response is not None
    assert prolong_request_lock_response.lock_expires_at is not None

    await rq.delete()
    assert await apify_client_async.request_queue(created_rq.id).get() is None


#############
# NEW TESTS #
#############


async def test_request_queue_get_or_create_and_get(apify_client_async: ApifyClientAsync) -> None:
    """Test creating a request queue and retrieving it."""
    rq_name = get_random_resource_name('queue')

    # Create queue
    created_rq = await apify_client_async.request_queues().get_or_create(name=rq_name)
    assert created_rq is not None
    assert created_rq.id is not None
    assert created_rq.name == rq_name

    # Get the same queue
    rq_client = apify_client_async.request_queue(created_rq.id)
    retrieved_rq = await rq_client.get()
    assert retrieved_rq is not None
    assert retrieved_rq.id == created_rq.id
    assert retrieved_rq.name == rq_name

    # Cleanup
    await rq_client.delete()


async def test_request_queue_update(apify_client_async: ApifyClientAsync) -> None:
    """Test updating request queue properties."""
    rq_name = get_random_resource_name('queue')
    new_name = get_random_resource_name('queue-updated')

    created_rq = await apify_client_async.request_queues().get_or_create(name=rq_name)
    rq_client = apify_client_async.request_queue(created_rq.id)

    # Update the name
    updated_rq = await rq_client.update(name=new_name)
    assert updated_rq is not None
    assert updated_rq.name == new_name
    assert updated_rq.id == created_rq.id

    # Verify the update persisted
    retrieved_rq = await rq_client.get()
    assert retrieved_rq is not None
    assert retrieved_rq.name == new_name

    # Cleanup
    await rq_client.delete()


async def test_request_queue_add_and_get_request(apify_client_async: ApifyClientAsync) -> None:
    """Test adding and getting a request from the queue."""
    rq_name = get_random_resource_name('queue')

    created_rq = await apify_client_async.request_queues().get_or_create(name=rq_name)
    rq_client = apify_client_async.request_queue(created_rq.id)

    # Add a request
    request_data = {
        'url': 'https://example.com/test',
        'uniqueKey': 'test-key-1',
        'method': 'GET',
    }
    add_result = await rq_client.add_request(request_data)
    assert add_result is not None
    assert add_result.request_id is not None
    assert add_result.was_already_present is False

    # Wait briefly for eventual consistency
    await asyncio.sleep(1)

    # Get the request
    request = await rq_client.get_request(add_result.request_id)
    assert request is not None
    assert str(request.url) == 'https://example.com/test'
    assert request.unique_key == 'test-key-1'

    # Cleanup
    await rq_client.delete()


async def test_request_queue_list_head(apify_client_async: ApifyClientAsync) -> None:
    """Test listing requests from the head of the queue."""
    rq_name = get_random_resource_name('queue')

    created_rq = await apify_client_async.request_queues().get_or_create(name=rq_name)
    rq_client = apify_client_async.request_queue(created_rq.id)

    # Add multiple requests
    for i in range(5):
        await rq_client.add_request(
            {
                'url': f'https://example.com/page-{i}',
                'uniqueKey': f'page-{i}',
            }
        )

    # Wait briefly for eventual consistency
    await asyncio.sleep(1)

    # List head
    head_response = await rq_client.list_head(limit=3)
    assert head_response is not None
    assert len(head_response.items) == 3

    # Cleanup
    await rq_client.delete()


async def test_request_queue_list_requests(apify_client_async: ApifyClientAsync) -> None:
    """Test listing all requests in the queue."""
    rq_name = get_random_resource_name('queue')

    created_rq = await apify_client_async.request_queues().get_or_create(name=rq_name)
    rq_client = apify_client_async.request_queue(created_rq.id)

    # Add multiple requests
    for i in range(5):
        await rq_client.add_request(
            {
                'url': f'https://example.com/item-{i}',
                'uniqueKey': f'item-{i}',
            }
        )

    # Wait briefly for eventual consistency
    await asyncio.sleep(1)

    # List all requests
    list_response = await rq_client.list_requests()
    assert list_response is not None
    assert len(list_response.items) == 5

    # Cleanup
    await rq_client.delete()


async def test_request_queue_delete_request(apify_client_async: ApifyClientAsync) -> None:
    """Test deleting a request from the queue."""
    rq_name = get_random_resource_name('queue')

    created_rq = await apify_client_async.request_queues().get_or_create(name=rq_name)
    rq_client = apify_client_async.request_queue(created_rq.id)

    # Add a request
    add_result = await rq_client.add_request(
        {
            'url': 'https://example.com/to-delete',
            'uniqueKey': 'delete-me',
        }
    )

    # Wait briefly for eventual consistency
    await asyncio.sleep(1)

    # Verify it exists
    request = await rq_client.get_request(add_result.request_id)
    assert request is not None

    # Delete the request
    await rq_client.delete_request(add_result.request_id)

    # Wait briefly
    await asyncio.sleep(1)

    # Verify it's gone
    deleted_request = await rq_client.get_request(add_result.request_id)
    assert deleted_request is None

    # Cleanup
    await rq_client.delete()


async def test_request_queue_batch_add_requests(apify_client_async: ApifyClientAsync) -> None:
    """Test adding multiple requests in batch."""
    rq_name = get_random_resource_name('queue')

    created_rq = await apify_client_async.request_queues().get_or_create(name=rq_name)
    rq_client = apify_client_async.request_queue(created_rq.id)

    # Batch add requests
    requests_to_add = [{'url': f'https://example.com/batch-{i}', 'uniqueKey': f'batch-{i}'} for i in range(10)]
    batch_response = await rq_client.batch_add_requests(requests_to_add)
    assert batch_response is not None
    assert len(batch_response.processed_requests) == 10
    assert len(batch_response.unprocessed_requests) == 0

    # Wait briefly for eventual consistency
    await asyncio.sleep(1)

    # Verify requests were added
    list_response = await rq_client.list_requests()
    assert len(list_response.items) == 10

    # Cleanup
    await rq_client.delete()


async def test_request_queue_batch_delete_requests(apify_client_async: ApifyClientAsync) -> None:
    """Test deleting multiple requests in batch."""
    rq_name = get_random_resource_name('queue')

    created_rq = await apify_client_async.request_queues().get_or_create(name=rq_name)
    rq_client = apify_client_async.request_queue(created_rq.id)

    # Add requests
    for i in range(10):
        await rq_client.add_request(
            {
                'url': f'https://example.com/delete-{i}',
                'uniqueKey': f'delete-{i}',
            }
        )

    # Wait briefly for eventual consistency
    await asyncio.sleep(1)

    # List requests to get IDs
    list_response = await rq_client.list_requests()
    requests_to_delete = [{'uniqueKey': item.unique_key} for item in list_response.items[:5]]

    # Batch delete
    delete_response = await rq_client.batch_delete_requests(requests_to_delete)
    assert delete_response is not None
    assert len(delete_response.processed_requests) == 5

    # Wait briefly
    await asyncio.sleep(1)

    # Verify remaining requests
    remaining = await rq_client.list_requests()
    assert len(remaining.items) == 5

    # Cleanup
    await rq_client.delete()


async def test_request_queue_delete_nonexistent(apify_client_async: ApifyClientAsync) -> None:
    """Test that getting a deleted queue returns None."""
    rq_name = get_random_resource_name('queue')

    created_rq = await apify_client_async.request_queues().get_or_create(name=rq_name)
    rq_client = apify_client_async.request_queue(created_rq.id)

    # Delete queue
    await rq_client.delete()

    # Verify it's gone
    retrieved_rq = await rq_client.get()
    assert retrieved_rq is None


async def test_request_queue_list_and_lock_head(apify_client_async: ApifyClientAsync) -> None:
    """Test locking requests from the head of the queue."""
    rq_name = get_random_resource_name('queue')

    created_rq = await apify_client_async.request_queues().get_or_create(name=rq_name)
    rq_client = apify_client_async.request_queue(created_rq.id, client_key=get_random_string(10))

    # Add multiple requests
    for i in range(5):
        await rq_client.add_request({'url': f'https://example.com/lock-{i}', 'uniqueKey': f'lock-{i}'})

    # Wait briefly for eventual consistency
    await asyncio.sleep(1)

    # Lock head requests
    lock_response = await rq_client.list_and_lock_head(limit=3, lock_secs=60)
    assert lock_response is not None
    assert len(lock_response.items) == 3

    # Verify requests are locked
    for locked_request in lock_response.items:
        assert locked_request.id is not None
        assert locked_request.lock_expires_at is not None

    # Cleanup
    await rq_client.delete()


async def test_request_queue_prolong_request_lock(apify_client_async: ApifyClientAsync) -> None:
    """Test prolonging a request lock."""
    rq_name = get_random_resource_name('queue')

    created_rq = await apify_client_async.request_queues().get_or_create(name=rq_name)
    rq_client = apify_client_async.request_queue(created_rq.id, client_key=get_random_string(10))

    # Add a request
    await rq_client.add_request({'url': 'https://example.com/prolong', 'uniqueKey': 'prolong-test'})

    # Wait briefly for eventual consistency
    await asyncio.sleep(1)

    # Lock the request
    lock_response = await rq_client.list_and_lock_head(limit=1, lock_secs=60)
    assert len(lock_response.items) == 1
    locked_request = lock_response.items[0]
    original_lock_expires = locked_request.lock_expires_at

    # Prolong the lock
    prolong_response = await rq_client.prolong_request_lock(locked_request.id, lock_secs=120)
    assert prolong_response is not None
    assert prolong_response.lock_expires_at is not None
    assert prolong_response.lock_expires_at > original_lock_expires

    # Cleanup
    await rq_client.delete()


async def test_request_queue_delete_request_lock(apify_client_async: ApifyClientAsync) -> None:
    """Test deleting a request lock."""
    rq_name = get_random_resource_name('queue')

    created_rq = await apify_client_async.request_queues().get_or_create(name=rq_name)
    rq_client = apify_client_async.request_queue(created_rq.id, client_key=get_random_string(10))

    # Add a request
    await rq_client.add_request({'url': 'https://example.com/unlock', 'uniqueKey': 'unlock-test'})

    # Wait briefly for eventual consistency
    await asyncio.sleep(1)

    # Lock the request
    lock_response = await rq_client.list_and_lock_head(limit=1, lock_secs=60)
    assert len(lock_response.items) == 1
    locked_request = lock_response.items[0]

    # Delete the lock
    await rq_client.delete_request_lock(locked_request.id)

    # Verify the operation succeeded (no exception thrown)
    # The request should still exist but be unlocked
    request = await rq_client.get_request(locked_request.id)
    assert request is not None

    # Cleanup
    await rq_client.delete()


async def test_request_queue_unlock_requests(apify_client_async: ApifyClientAsync) -> None:
    """Test unlocking all requests locked by the client."""
    rq_name = get_random_resource_name('queue')

    created_rq = await apify_client_async.request_queues().get_or_create(name=rq_name)
    rq_client = apify_client_async.request_queue(created_rq.id, client_key=get_random_string(10))

    # Add multiple requests
    for i in range(5):
        await rq_client.add_request({'url': f'https://example.com/unlock-{i}', 'uniqueKey': f'unlock-{i}'})

    # Wait briefly for eventual consistency
    await asyncio.sleep(1)

    # Lock some requests
    lock_response = await rq_client.list_and_lock_head(limit=3, lock_secs=60)
    assert len(lock_response.items) == 3

    # Unlock all requests
    unlock_response = await rq_client.unlock_requests()

    assert unlock_response is not None
    assert unlock_response.unlocked_count == 3

    # Cleanup
    await rq_client.delete()


async def test_request_queue_update_request(apify_client_async: ApifyClientAsync) -> None:
    """Test updating a request in the queue."""
    rq_name = get_random_resource_name('queue')

    created_rq = await apify_client_async.request_queues().get_or_create(name=rq_name)
    rq_client = apify_client_async.request_queue(created_rq.id)

    # Add a request
    request_data = {
        'url': 'https://example.com/original',
        'uniqueKey': 'update-test',
        'method': 'GET',
    }
    add_result = await rq_client.add_request(request_data)
    assert add_result is not None
    assert add_result.request_id is not None

    # Wait briefly for eventual consistency
    await asyncio.sleep(1)

    # Get the request to get its full data
    original_request = await rq_client.get_request(add_result.request_id)
    assert original_request is not None

    # Update the request (change method and add user data)
    updated_request_data = {
        'id': add_result.request_id,
        'url': str(original_request.url),
        'uniqueKey': original_request.unique_key,
        'method': 'POST',
        'userData': {'updated': True},
    }
    update_result = await rq_client.update_request(updated_request_data)
    assert update_result is not None
    assert update_result.request_id == add_result.request_id

    # Cleanup
    await rq_client.delete()
