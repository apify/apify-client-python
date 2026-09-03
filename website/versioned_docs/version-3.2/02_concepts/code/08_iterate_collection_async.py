from apify_client import ApifyClientAsync

TOKEN = 'MY-APIFY-TOKEN'


async def main() -> None:
    apify_client = ApifyClientAsync(TOKEN)

    # Iterate over all Actors owned by the current user, lazily fetching
    # as many pages as needed under the hood.
    async for actor in apify_client.actors().iterate(my=True):
        print(actor.id)
