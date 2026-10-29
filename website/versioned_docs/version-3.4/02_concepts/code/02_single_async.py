from apify_client import ApifyClientAsync

TOKEN = 'MY-APIFY-TOKEN'


async def main() -> None:
    apify_client = ApifyClientAsync(TOKEN)

    # Resource clients accept an ID of the resource
    actor_client = apify_client.actor('username/actor-name')

    # Fetch the 'username/actor-name' object from the API
    my_actor = await actor_client.get()

    # Start the run of 'username/actor-name' and return the Run object
    my_actor_run = await actor_client.start()
