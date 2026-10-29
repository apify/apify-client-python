from apify_client import ApifyClientAsync

TOKEN = 'MY-APIFY-TOKEN'


async def main() -> None:
    apify_client = ApifyClientAsync(TOKEN)
    server_client = apify_client.actor('username/actor-name').server()

    # Send a GET request to the /search endpoint of the Actor's server.
    response = await server_client.request('/search', params={'q': 'apify'})
    print(response.json())

    # Send a POST request with a JSON body.
    response = await server_client.request(
        '/items',
        method='POST',
        json={'url': 'https://apify.com'},
    )
    print(response.status_code)
