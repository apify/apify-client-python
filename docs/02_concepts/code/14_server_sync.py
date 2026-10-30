from http import HTTPStatus

from apify_client import ApifyClient

TOKEN = 'MY-APIFY-TOKEN'


def main() -> None:
    apify_client = ApifyClient(TOKEN)
    actor_server_client = apify_client.actor('username/actor-name').server()

    # Send a GET request to the /search endpoint of the Actor's server. The method
    # returns error responses too, so check the status first.
    response = actor_server_client.request('/search', params={'q': 'apify'})
    if response.status_code != HTTPStatus.OK:
        raise RuntimeError(f'Search failed with status {response.status_code}')
    print(response.json())

    # Send a POST request with a JSON body.
    response = actor_server_client.request(
        '/items',
        method='POST',
        json={'url': 'https://apify.com'},
    )
    print(response.status_code)
