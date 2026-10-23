from apify_client import ApifyClientAsync

TOKEN = 'MY-APIFY-TOKEN'


async def main() -> None:
    apify_client = ApifyClientAsync(TOKEN)
    actor_client = apify_client.actor('username/actor-name')

    # Send a GET request to the /search endpoint of the Actor's server.
    response = await actor_client.server_request('/search', params={'q': 'apify'})
    print(response.json())

    # Send a POST request with a JSON body.
    response = await actor_client.server_request(
        '/items',
        method='POST',
        json={'url': 'https://apify.com'},
    )
    print(response.status_code)
