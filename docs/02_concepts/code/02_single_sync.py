from apify_client import ApifyClient

TOKEN = 'MY-APIFY-TOKEN'


def main() -> None:
    apify_client = ApifyClient(token=TOKEN)

    # Resource clients accept an ID of the resource
    actor_client = apify_client.actor(actor_id='username/actor-name')

    # Fetch the 'username/actor-name' object from the API
    my_actor = actor_client.get()

    # Start the run of 'username/actor-name' and return the Run object
    my_actor_run = actor_client.start()
