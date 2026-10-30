from apify_client import ApifyClient

TOKEN = 'MY-APIFY-TOKEN'


def main() -> None:
    apify_client = ApifyClient(TOKEN)
    actor_server_client = apify_client.actor('username/actor-name').server()

    # Get the URL of the Actor's server.
    server_url = actor_server_client.get_url()
    print(server_url)

    # Get the OpenAPI specification and list the server's endpoints.
    spec = actor_server_client.get_openapi_spec()
    if spec is not None:
        print(list(spec['paths']))
