from apify_client import ApifyClient

TOKEN = 'MY-APIFY-TOKEN'


def main() -> None:
    apify_client = ApifyClient(TOKEN)

    # Collection clients do not require a parameter
    actor_collection_client = apify_client.actors()

    # Create an Actor with the name: my-actor
    my_actor = actor_collection_client.create(name='my-actor')

    # List all of your Actors
    actor_list = actor_collection_client.list().items
