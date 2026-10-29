from apify_client import ApifyClient

TOKEN = 'MY-APIFY-TOKEN'


def main() -> None:
    apify_client = ApifyClient(TOKEN)
    server_client = apify_client.actor('username/actor-name').server()

    # Send a GET request to the /search endpoint of the Actor's server.
    response = server_client.request('/search', params={'q': 'apify'})
    print(response.json())

    # Send a POST request with a JSON body.
    response = server_client.request(
        '/items',
        method='POST',
        json={'url': 'https://apify.com'},
    )
    print(response.status_code)
