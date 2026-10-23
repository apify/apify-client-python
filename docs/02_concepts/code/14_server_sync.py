from apify_client import ApifyClient

TOKEN = 'MY-APIFY-TOKEN'


def main() -> None:
    apify_client = ApifyClient(TOKEN)
    actor_client = apify_client.actor('username/actor-name')

    # Send a GET request to the /search endpoint of the Actor's server.
    response = actor_client.server_request('/search', params={'q': 'apify'})
    print(response.json())

    # Send a POST request with a JSON body.
    response = actor_client.server_request(
        '/items',
        method='POST',
        json={'url': 'https://apify.com'},
    )
    print(response.status_code)
