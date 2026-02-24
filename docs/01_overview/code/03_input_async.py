from apify_client import ApifyClientAsync

TOKEN = 'MY-APIFY-TOKEN'


async def main() -> None:
    apify_client = ApifyClientAsync(token=TOKEN)
    actor_client = apify_client.actor(actor_id='username/actor-name')

    # Define the input for the Actor.
    run_input = {
        'some': 'input',
    }

    # Start an Actor and waits for it to finish.
    call_result = await actor_client.call(run_input=run_input)
