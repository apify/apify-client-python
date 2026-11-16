from apify_client import ApifyClient

TOKEN = 'MY-APIFY-TOKEN'


def main() -> None:
    apify_client = ApifyClient(TOKEN)

    apify_client.actor('username/actor-name').call()

    stats = apify_client.stats
    print(f'API calls: {stats.calls}, HTTP requests: {stats.requests}')
    print(f'Rate limit errors per attempt: {dict(stats.rate_limit_errors)}')
