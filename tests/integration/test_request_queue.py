from __future__ import annotations

from typing import TYPE_CHECKING

from integration.integration_test_utils import random_resource_name, random_string

if TYPE_CHECKING:
    from apify_client import ApifyClient, ApifyClientAsync


def test_request_queue_lock_sync(apify_client: ApifyClient) -> None:
    created_rq = apify_client.request_queues().get_or_create(name=random_resource_name('queue'))
    rq = apify_client.request_queue(created_rq.id, client_key=random_string(10))

    # Add requests and check if correct number of requests was locked
    for i in range(15):
        rq.add_request({'url': f'http://test-lock.com/{i}', 'uniqueKey': f'http://test-lock.com/{i}'})

    get_head_and_lock_response = rq.list_and_lock_head(limit=10, lock_secs=10)

    for locked_request in get_head_and_lock_response.data.items:
        assert locked_request.lock_expires_at is not None

    # Check if the delete request works
    rq.delete_request_lock(get_head_and_lock_response.data.items[1].id)

    """This is probably not working:
    delete_lock_request = rq.get_request(get_head_and_lock_response.data.items[1].id)
    assert delete_lock_request is not None
    assert delete_lock_request.lock_expires_at is None
    """

    rq.delete_request_lock(get_head_and_lock_response.data.items[2].id, forefront=True)

    """This is probably not working:
    delete_lock_request2 = rq.get_request(get_head_and_lock_response.data.items[2].id)
    assert delete_lock_request2 is not None
    assert delete_lock_request2.lock_expires_at is None
    """

    # Check if the prolong request works
    prolong_request_lock_response = rq.prolong_request_lock(
        get_head_and_lock_response.data.items[3].id,
        lock_secs=15,
    )
    assert prolong_request_lock_response.data is not None
    assert prolong_request_lock_response.data.lock_expires_at is not None

    rq.delete()
    assert apify_client.request_queue(created_rq.id).get() is None


def test_request_batch_operations_sync(apify_client: ApifyClient) -> None:
    created_rq = apify_client.request_queues().get_or_create(name=random_resource_name('queue'))
    rq = apify_client.request_queue(created_rq.id)

    # Add requests to queue and check if they were added
    requests_to_add = [
        {'url': f'http://test-batch.com/{i}', 'uniqueKey': f'http://test-batch.com/{i}'} for i in range(25)
    ]

    batch_response = rq.batch_add_requests(requests_to_add)
    assert len(batch_response.data.processed_requests or []) > 0

    list_requests_response = rq.list_requests()
    assert len(list_requests_response.data.items) == len(batch_response.data.processed_requests or [])

    # Delete requests from queue and check if they were deleted
    requests_to_delete = list_requests_response.data.items[:20]
    delete_response = rq.batch_delete_requests([{'uniqueKey': req.unique_key} for req in requests_to_delete])
    requests_in_queue2 = rq.list_requests()
    assert len(requests_in_queue2.data.items) == 25 - len(delete_response.data.processed_requests or [])

    rq.delete()


async def test_request_queue_lock_async(apify_client_async: ApifyClientAsync) -> None:
    created_rq = await apify_client_async.request_queues().get_or_create(name=random_resource_name('queue'))
    rq = apify_client_async.request_queue(created_rq.id, client_key=random_string(10))

    # Add requests and check if correct number of requests was locked
    for i in range(15):
        await rq.add_request({'url': f'http://test-lock.com/{i}', 'uniqueKey': f'http://test-lock.com/{i}'})

    get_head_and_lock_response = await rq.list_and_lock_head(limit=10, lock_secs=10)

    for locked_request in get_head_and_lock_response.data.items:
        assert locked_request.lock_expires_at is not None

    # Check if the delete request works
    await rq.delete_request_lock(get_head_and_lock_response.data.items[1].id)

    """This is probably not working:
    delete_lock_request = await rq.get_request(get_head_and_lock_response.data.items[1].id)
    assert delete_lock_request is not None
    assert delete_lock_request.lock_expires_at is None
    """

    await rq.delete_request_lock(get_head_and_lock_response.data.items[2].id, forefront=True)

    """This is probably not working:
    delete_lock_request2 = await rq.get_request(get_head_and_lock_response.data.items[2].id)
    assert delete_lock_request2 is not None
    assert delete_lock_request2.lock_expires_at is None
    """

    # Check if the prolong request works
    prolong_request_lock_response = await rq.prolong_request_lock(
        get_head_and_lock_response.data.items[3].id,
        lock_secs=15,
    )
    assert prolong_request_lock_response.data is not None
    assert prolong_request_lock_response.data.lock_expires_at is not None

    await rq.delete()
    assert await apify_client_async.request_queue(created_rq.id).get() is None


async def test_request_batch_operations_async(apify_client_async: ApifyClientAsync) -> None:
    created_rq = await apify_client_async.request_queues().get_or_create(name=random_resource_name('queue'))
    rq = apify_client_async.request_queue(created_rq.id)

    # Add requests to queue and check if they were added
    requests_to_add = [
        {
            'url': f'http://test-batch.com/{i}',
            'uniqueKey': f'http://test-batch.com/{i}',
        }
        for i in range(25)
    ]

    batch_response = await rq.batch_add_requests(requests_to_add)
    assert len(batch_response.data.processed_requests or []) > 0

    requests_in_queue = await rq.list_requests()
    assert len(requests_in_queue.data.items) == len(batch_response.data.processed_requests or [])

    # Delete requests from queue and check if they were deleted
    requests_to_delete = requests_in_queue.data.items[:20]
    delete_response = await rq.batch_delete_requests([{'uniqueKey': req.unique_key} for req in requests_to_delete])
    requests_in_queue2 = await rq.list_requests()
    assert len(requests_in_queue2.data.items) == 25 - len(delete_response.data.processed_requests or [])

    await rq.delete()
