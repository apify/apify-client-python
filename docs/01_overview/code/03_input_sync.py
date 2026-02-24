from apify_client import ApifyClient

TOKEN = 'MY-APIFY-TOKEN'


def main() -> None:
    apify_client = ApifyClient(token=TOKEN)
    actor_client = apify_client.actor(actor_id='username/actor-name')

    # Define the input for the Actor.
    run_input = {
        'some': 'input',
    }

    # Start an Actor and waits for it to finish.
    call_result = actor_client.call(run_input=run_input)
