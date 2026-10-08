from apify_client import ApifyClientAsync

TOKEN = 'MY-APIFY-TOKEN'


async def main() -> None:
    apify_client = ApifyClientAsync(TOKEN)
    rq_client = apify_client.request_queue('REQUEST-QUEUE-ID')

    # Plain dict — keys may be snake_case or camelCase.
    await rq_client.add_request(
        {
            'url': 'https://example.com',
            'unique_key': 'https://example.com',
            'method': 'GET',
        }
    )
