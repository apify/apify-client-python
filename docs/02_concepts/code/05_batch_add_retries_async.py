from datetime import timedelta

from apify_client import ApifyClientAsync

TOKEN = 'MY-APIFY-TOKEN'


async def main() -> None:
    apify_client = ApifyClientAsync(TOKEN)
    rq_client = apify_client.request_queue('my-request-queue-id')

    result = await rq_client.batch_add_requests(
        [{'unique_key': 'https://example.com', 'url': 'https://example.com'}],
        max_unprocessed_requests_retries=5,
        min_delay_between_unprocessed_requests_retries=timedelta(seconds=1),
    )

    for request in result.unprocessed_requests:
        print(f'Not added: {request.url}')
