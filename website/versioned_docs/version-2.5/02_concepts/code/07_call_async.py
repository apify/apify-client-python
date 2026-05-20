from apify_client import ApifyClientAsync

TOKEN = 'MY-APIFY-TOKEN'


async def main() -> None:
    apify_client = ApifyClientAsync(TOKEN)
    actor_client = apify_client.actor('username/actor-name')

    # Start an Actor and waits for it to finish
    finished_actor_run = await actor_client.call()

    # Starts an Actor and waits maximum 60s (1 minute) for the finish
    actor_run = await actor_client.start(wait_for_finish=60)
