import httpx2

from apify_client import ApifyClient

TOKEN = 'MY-APIFY-TOKEN'


def main() -> None:
    apify_client = ApifyClient(TOKEN)
    actor_client = apify_client.actor('username/actor-name')

    # Get the server's URL and the OpenAPI specification of its endpoints.
    server_url = actor_client.get_server_url()
    spec = actor_client.get_server_openapi_spec()
    if spec is not None:
        print(list(spec['paths']))

    # The first request to an idle Actor waits for a server run to start.
    with httpx2.Client(
        base_url=server_url,
        headers={'Authorization': f'Bearer {TOKEN}'},
        timeout=360,
    ) as http_client:
        response = http_client.get('/search', params={'q': 'apify'})
        print(response.json())
