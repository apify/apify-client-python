from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from integration.integration_test_utils import random_resource_name, random_string

from apify_client.clients.resource_clients.request_queue import unique_key_to_request_id

if TYPE_CHECKING:
    from apify_client import ApifyClient, ApifyClientAsync


class TestRequestQueueSync:
    def test_request_queue_lock(self, apify_client: ApifyClient) -> None:
        created_queue = apify_client.request_queues().get_or_create(name=random_resource_name('queue'))
        queue = apify_client.request_queue(created_queue['id'], client_key=random_string(10))

        # Add requests and check if correct number of requests was locked
        for i in range(15):
            queue.add_request({'url': f'http://test-lock.com/{i}', 'uniqueKey': f'http://test-lock.com/{i}'})
        locked_requests_list = queue.list_and_lock_head(limit=10, lock_secs=10)
        locked_requests = locked_requests_list['items']
        for locked_request in locked_requests:
            assert locked_request['lockExpiresAt'] is not None

        # Check if the delete request works
        queue.delete_request_lock(locked_requests[1]['id'])
        delete_lock_request = queue.get_request(locked_requests[1]['id'])
        assert delete_lock_request is not None
        assert delete_lock_request.get('lockExpiresAt') is None
        queue.delete_request_lock(locked_requests[2]['id'], forefront=True)
        delete_lock_request2 = queue.get_request(locked_requests[2]['id'])
        assert delete_lock_request2 is not None
        assert delete_lock_request2.get('lockExpiresAt') is None

        # Check if the prolong request works
        assert queue.prolong_request_lock(locked_requests[3]['id'], lock_secs=15)['lockExpiresAt'] is not None

        queue.delete()
        assert apify_client.request_queue(created_queue['id']).get() is None

    def test_request_batch_operations(self, apify_client: ApifyClient) -> None:
        created_queue = apify_client.request_queues().get_or_create(name=random_resource_name('queue'))
        queue = apify_client.request_queue(created_queue['id'])

        # Add requests to queue and check if they were added
        requests_to_add = [
            {'url': f'http://test-batch.com/{i}', 'uniqueKey': f'http://test-batch.com/{i}'} for i in range(25)
        ]
        added_requests = queue.batch_add_requests(requests_to_add)
        assert len(added_requests.get('processedRequests', [])) > 0
        requests_in_queue = queue.list_requests()
        assert len(requests_in_queue['items']) == len(added_requests['processedRequests'])

        # Delete requests from queue and check if they were deleted
        requests_to_delete = requests_in_queue['items'][:20]
        delete_response = queue.batch_delete_requests(
            [{'uniqueKey': req.get('uniqueKey')} for req in requests_to_delete]
        )
        requests_in_queue2 = queue.list_requests()
        assert len(requests_in_queue2['items']) == 25 - len(delete_response['processedRequests'])

        queue.delete()


class TestRequestQueueAsync:
    async def test_request_queue_lock(self, apify_client_async: ApifyClientAsync) -> None:
        created_queue = await apify_client_async.request_queues().get_or_create(name=random_resource_name('queue'))
        queue = apify_client_async.request_queue(created_queue['id'], client_key=random_string(10))

        # Add requests and check if correct number of requests was locked
        for i in range(15):
            await queue.add_request({'url': f'http://test-lock.com/{i}', 'uniqueKey': f'http://test-lock.com/{i}'})
        locked_requests_list = await queue.list_and_lock_head(limit=10, lock_secs=10)
        locked_requests = locked_requests_list['items']
        for locked_request in locked_requests:
            assert locked_request['lockExpiresAt'] is not None

        # Check if the delete request works
        await queue.delete_request_lock(locked_requests[1]['id'])
        delete_lock_request = await queue.get_request(locked_requests[1]['id'])
        assert delete_lock_request is not None
        assert delete_lock_request.get('lockExpiresAt') is None
        await queue.delete_request_lock(locked_requests[2]['id'], forefront=True)
        delete_lock_request2 = await queue.get_request(locked_requests[2]['id'])
        assert delete_lock_request2 is not None
        assert delete_lock_request2.get('lockExpiresAt') is None

        # Check if the prolong request works
        prolonged_request = await queue.prolong_request_lock(locked_requests[3]['id'], lock_secs=15)
        assert prolonged_request['lockExpiresAt'] is not None

        await queue.delete()
        assert await apify_client_async.request_queue(created_queue['id']).get() is None

    async def test_request_batch_operations(self, apify_client_async: ApifyClientAsync) -> None:
        created_queue = await apify_client_async.request_queues().get_or_create(name=random_resource_name('queue'))
        queue = apify_client_async.request_queue(created_queue['id'])

        # Add requests to queue and check if they were added
        requests_to_add = [
            {'url': f'http://test-batch.com/{i}', 'uniqueKey': f'http://test-batch.com/{i}'} for i in range(25)
        ]
        added_requests = await queue.batch_add_requests(requests_to_add)
        assert len(added_requests.get('processedRequests', [])) > 0
        requests_in_queue = await queue.list_requests()
        assert len(requests_in_queue['items']) == len(added_requests['processedRequests'])

        # Delete requests from queue and check if they were deleted
        requests_to_delete = requests_in_queue['items'][:20]
        delete_response = await queue.batch_delete_requests(
            [{'uniqueKey': req.get('uniqueKey')} for req in requests_to_delete]
        )
        requests_in_queue2 = await queue.list_requests()
        assert len(requests_in_queue2['items']) == 25 - len(delete_response['processedRequests'])

        await queue.delete()


def test_unique_key_to_request_id_length() -> None:
    unique_key = 'exampleKey123'
    request_id = unique_key_to_request_id(unique_key, request_id_length=15)
    assert len(request_id) == 15, 'Request ID should have the correct length.'


def test_unique_key_to_request_id_consistency() -> None:
    unique_key = 'consistentKey'
    request_id_1 = unique_key_to_request_id(unique_key)
    request_id_2 = unique_key_to_request_id(unique_key)
    assert request_id_1 == request_id_2, 'The same unique key should generate consistent request IDs.'


@pytest.mark.parametrize(
    ('unique_key', 'expected_request_id'),
    [
        ('abc', 'ungWv48BzpBQUDe'),
        ('uniqueKey', 'xiWPs083cree7mH'),
        ('', '47DEQpj8HBSaTIm'),
        ('测试中文', 'lKPdJkdvw8MXEUp'),
        ('test+/=', 'XZRQjhoG0yjfnYD'),
    ],
    ids=[
        'basic_abc',
        'keyword_uniqueKey',
        'empty_string',
        'non_ascii_characters',
        'url_unsafe_characters',
    ],
)
def test_unique_key_to_request_id_matches_known_values(unique_key: str, expected_request_id: str) -> None:
    request_id = unique_key_to_request_id(unique_key)
    assert request_id == expected_request_id, f'Unique key "{unique_key}" should produce the expected request ID.'
