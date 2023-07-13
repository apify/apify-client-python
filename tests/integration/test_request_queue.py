import random
import string

from apify_client import ApifyClient, ApifyClientAsync


def random_string(length: int = 10) -> str:
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))


def random_queue_name() -> str:
    return f'python-client-test-queue-{random_string(5)}'


class TestRequestQueueSync:
    def test_request_queue_lock(self, apify_client: ApifyClient) -> None:
        created_queue = apify_client.request_queues().get_or_create(name=random_queue_name())
        queue = apify_client.request_queue(created_queue['id'], client_key=random_string(10))
        for i in range(15):
            queue.add_request({'url': f'http://example.com3{i}', 'uniqueKey': f'http://example.com3{i}'})
        locked_requests_list = queue.list_and_lock_head(limit=10, lock_secs=10)
        locked_requests = locked_requests_list['items']
        for locked_request in locked_requests:
            assert locked_request['lockExpiresAt'] is not None
        queue.delete_request_lock(locked_requests[1]['id'])
        delete_lock_request = queue.get_request(locked_requests[1]['id'])
        assert delete_lock_request.get('lockExpiresAt') is None  # type: ignore
        queue.delete_request_lock(locked_requests[2]['id'], forefront=True)
        delete_lock_request2 = queue.get_request(locked_requests[2]['id'])
        assert delete_lock_request2.get('lockExpiresAt') is None  # type: ignore
        assert queue.prolong_request_lock(locked_requests[3]['id'], lock_secs=15)['lockExpiresAt'] is not None
        queue.delete()
        assert apify_client.request_queue(created_queue['id']).get() is None


class TestRequestQueueAsync:
    async def test_request_queue_lock(self, apify_client_async: ApifyClientAsync) -> None:
        created_queue = await apify_client_async.request_queues().get_or_create(name=random_queue_name())
        queue = apify_client_async.request_queue(created_queue['id'], client_key=random_string(10))
        for i in range(15):
            await queue.add_request({'url': f'http://example.com3{i}', 'uniqueKey': f'http://example.com3{i}'})
        locked_requests_list = await queue.list_and_lock_head(limit=10, lock_secs=10)
        locked_requests = locked_requests_list['items']
        for locked_request in locked_requests:
            assert locked_request['lockExpiresAt'] is not None
        await queue.delete_request_lock(locked_requests[1]['id'])
        delete_lock_request = await queue.get_request(locked_requests[1]['id'])
        assert delete_lock_request.get('lockExpiresAt') is None  # type: ignore
        await queue.delete_request_lock(locked_requests[2]['id'], forefront=True)
        delete_lock_request2 = await queue.get_request(locked_requests[2]['id'])
        assert delete_lock_request2.get('lockExpiresAt') is None  # type: ignore
        prolonged_request = await queue.prolong_request_lock(locked_requests[3]['id'], lock_secs=15)
        assert prolonged_request['lockExpiresAt'] is not None
        await queue.delete()
        assert await apify_client_async.request_queue(created_queue['id']).get() is None
