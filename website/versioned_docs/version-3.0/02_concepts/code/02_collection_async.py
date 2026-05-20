from apify_client import ApifyClientAsync

TOKEN = 'MY-APIFY-TOKEN'


async def main() -> None:
    apify_client = ApifyClientAsync(TOKEN)

    # Collection clients do not require a parameter
    actor_collection_client = apify_client.actors()

    # Create an Actor with the name: my-actor
    my_actor = await actor_collection_client.create(name='my-actor')

    # List all of your Actors
    actor_list = (await actor_collection_client.list()).items
