from __future__ import annotations

import time
from typing import TYPE_CHECKING

from .utils import get_random_resource_name, get_random_string

if TYPE_CHECKING:
    from apify_client import ApifyClient

##################################################
# OLD TESTS - Tests with mocks and signed URLs
##################################################


def test_request_queue_lock(apify_client: ApifyClient) -> None:
    created_rq = apify_client.request_queues().get_or_create(name=get_random_resource_name('queue'))
    rq = apify_client.request_queue(created_rq.id, client_key=get_random_string(10))

    # Add requests and check if correct number of requests was locked
    for i in range(15):
        rq.add_request({'url': f'http://test-lock.com/{i}', 'uniqueKey': f'http://test-lock.com/{i}'})

    get_head_and_lock_response = rq.list_and_lock_head(limit=10, lock_secs=10)

    for locked_request in get_head_and_lock_response.items:
        assert locked_request.lock_expires_at is not None

    # Check if the delete request works
    rq.delete_request_lock(get_head_and_lock_response.items[1].id)

    """This is probably not working:
    delete_lock_request = rq.get_request(get_head_and_lock_response.items[1].id)
    assert delete_lock_request is not None
    assert delete_lock_request.lock_expires_at is None
    """

    rq.delete_request_lock(get_head_and_lock_response.items[2].id, forefront=True)

    """This is probably not working:
    delete_lock_request2 = rq.get_request(get_head_and_lock_response.items[2].id)
    assert delete_lock_request2 is not None
    assert delete_lock_request2.lock_expires_at is None
    """

    # Check if the prolong request works
    prolong_request_lock_response = rq.prolong_request_lock(
        get_head_and_lock_response.items[3].id,
        lock_secs=15,
    )
    assert prolong_request_lock_response is not None
    assert prolong_request_lock_response.lock_expires_at is not None

    rq.delete()
    assert apify_client.request_queue(created_rq.id).get() is None


##################################################
# NEW TESTS - Basic CRUD operations without mocks
##################################################


def test_request_queue_get_or_create_and_get(apify_client: ApifyClient) -> None:
    """Test creating a request queue and retrieving it."""
    queue_name = get_random_resource_name('queue')

    # Create queue
    created_queue = apify_client.request_queues().get_or_create(name=queue_name)
    assert created_queue is not None
    assert created_queue.id is not None
    assert created_queue.name == queue_name

    # Get the same queue
    queue_client = apify_client.request_queue(created_queue.id)
    retrieved_queue = queue_client.get()
    assert retrieved_queue is not None
    assert retrieved_queue.id == created_queue.id
    assert retrieved_queue.name == queue_name

    # Cleanup
    queue_client.delete()


def test_request_queue_update(apify_client: ApifyClient) -> None:
    """Test updating request queue properties."""
    queue_name = get_random_resource_name('queue')
    new_name = get_random_resource_name('queue-updated')

    created_queue = apify_client.request_queues().get_or_create(name=queue_name)
    queue_client = apify_client.request_queue(created_queue.id)

    # Update the name
    updated_queue = queue_client.update(name=new_name)
    assert updated_queue is not None
    assert updated_queue.name == new_name
    assert updated_queue.id == created_queue.id

    # Verify the update persisted
    retrieved_queue = queue_client.get()
    assert retrieved_queue is not None
    assert retrieved_queue.name == new_name

    # Cleanup
    queue_client.delete()


def test_request_queue_add_and_get_request(apify_client: ApifyClient) -> None:
    """Test adding and getting a request from the queue."""
    queue_name = get_random_resource_name('queue')

    created_queue = apify_client.request_queues().get_or_create(name=queue_name)
    queue_client = apify_client.request_queue(created_queue.id)

    # Add a request
    request_data = {
        'url': 'https://example.com/test',
        'uniqueKey': 'test-key-1',
        'method': 'GET',
    }
    add_result = queue_client.add_request(request_data)
    assert add_result is not None
    assert add_result.request_id is not None
    assert add_result.was_already_present is False

    # Wait briefly for eventual consistency
    time.sleep(1)

    # Get the request
    request = queue_client.get_request(add_result.request_id)
    assert request is not None
    assert request.url == 'https://example.com/test'
    assert request.unique_key == 'test-key-1'

    # Cleanup
    queue_client.delete()


def test_request_queue_list_head(apify_client: ApifyClient) -> None:
    """Test listing requests from the head of the queue."""
    queue_name = get_random_resource_name('queue')

    created_queue = apify_client.request_queues().get_or_create(name=queue_name)
    queue_client = apify_client.request_queue(created_queue.id)

    # Add multiple requests
    for i in range(5):
        queue_client.add_request(
            {
                'url': f'https://example.com/page-{i}',
                'uniqueKey': f'page-{i}',
            }
        )

    # Wait briefly for eventual consistency
    time.sleep(1)

    # List head
    head_response = queue_client.list_head(limit=3)
    assert head_response is not None
    assert len(head_response.items) == 3

    # Cleanup
    queue_client.delete()


def test_request_queue_list_requests(apify_client: ApifyClient) -> None:
    """Test listing all requests in the queue."""
    queue_name = get_random_resource_name('queue')

    created_queue = apify_client.request_queues().get_or_create(name=queue_name)
    queue_client = apify_client.request_queue(created_queue.id)

    # Add multiple requests
    for i in range(5):
        queue_client.add_request(
            {
                'url': f'https://example.com/item-{i}',
                'uniqueKey': f'item-{i}',
            }
        )

    # Wait briefly for eventual consistency
    time.sleep(1)

    # List all requests
    list_response = queue_client.list_requests()
    assert list_response is not None
    assert len(list_response.items) == 5

    # Cleanup
    queue_client.delete()


def test_request_queue_delete_request(apify_client: ApifyClient) -> None:
    """Test deleting a request from the queue."""
    queue_name = get_random_resource_name('queue')

    created_queue = apify_client.request_queues().get_or_create(name=queue_name)
    queue_client = apify_client.request_queue(created_queue.id)

    # Add a request
    add_result = queue_client.add_request(
        {
            'url': 'https://example.com/to-delete',
            'uniqueKey': 'delete-me',
        }
    )

    # Wait briefly for eventual consistency
    time.sleep(1)

    # Verify it exists
    request = queue_client.get_request(add_result.request_id)
    assert request is not None

    # Delete the request
    queue_client.delete_request(add_result.request_id)

    # Wait briefly
    time.sleep(1)

    # Verify it's gone
    deleted_request = queue_client.get_request(add_result.request_id)
    assert deleted_request is None

    # Cleanup
    queue_client.delete()


def test_request_queue_batch_add_requests(apify_client: ApifyClient) -> None:
    """Test adding multiple requests in batch."""
    queue_name = get_random_resource_name('queue')

    created_queue = apify_client.request_queues().get_or_create(name=queue_name)
    queue_client = apify_client.request_queue(created_queue.id)

    # Batch add requests
    requests_to_add = [{'url': f'https://example.com/batch-{i}', 'uniqueKey': f'batch-{i}'} for i in range(10)]
    batch_response = queue_client.batch_add_requests(requests_to_add)
    assert batch_response is not None
    assert len(batch_response.processed_requests) == 10
    assert len(batch_response.unprocessed_requests) == 0

    # Wait briefly for eventual consistency
    time.sleep(1)

    # Verify requests were added
    list_response = queue_client.list_requests()
    assert len(list_response.items) == 10

    # Cleanup
    queue_client.delete()


def test_request_queue_batch_delete_requests(apify_client: ApifyClient) -> None:
    """Test deleting multiple requests in batch."""
    queue_name = get_random_resource_name('queue')

    created_queue = apify_client.request_queues().get_or_create(name=queue_name)
    queue_client = apify_client.request_queue(created_queue.id)

    # Add requests
    for i in range(10):
        queue_client.add_request(
            {
                'url': f'https://example.com/delete-{i}',
                'uniqueKey': f'delete-{i}',
            }
        )

    # Wait briefly for eventual consistency
    time.sleep(1)

    # List requests to get IDs
    list_response = queue_client.list_requests()
    requests_to_delete = [{'uniqueKey': item.unique_key} for item in list_response.items[:5]]

    # Batch delete
    delete_response = queue_client.batch_delete_requests(requests_to_delete)
    assert delete_response is not None
    assert len(delete_response.processed_requests) == 5

    # Wait briefly
    time.sleep(1)

    # Verify remaining requests
    remaining = queue_client.list_requests()
    assert len(remaining.items) == 5

    # Cleanup
    queue_client.delete()


def test_request_queue_delete_nonexistent(apify_client: ApifyClient) -> None:
    """Test that getting a deleted queue returns None."""
    queue_name = get_random_resource_name('queue')

    created_queue = apify_client.request_queues().get_or_create(name=queue_name)
    queue_client = apify_client.request_queue(created_queue.id)

    # Delete queue
    queue_client.delete()

    # Verify it's gone
    retrieved_queue = queue_client.get()
    assert retrieved_queue is None
