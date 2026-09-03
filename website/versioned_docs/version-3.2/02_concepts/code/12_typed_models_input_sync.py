from apify_client import ApifyClient

TOKEN = 'MY-APIFY-TOKEN'


def main() -> None:
    apify_client = ApifyClient(TOKEN)
    rq_client = apify_client.request_queue('REQUEST-QUEUE-ID')

    # Plain dict — keys may be snake_case or camelCase.
    rq_client.add_request(
        {
            'url': 'https://example.com',
            'unique_key': 'https://example.com',
            'method': 'GET',
        }
    )
