from apify_client import ApifyClient

TOKEN = 'MY-APIFY-TOKEN'


def main() -> None:
    apify_client = ApifyClient(TOKEN)

    actor_client = apify_client.actor('username/actor-name')
    runs_client = actor_client.runs()

    # List the last 10 runs of the Actor
    actor_runs = runs_client.list(limit=10, desc=True).items

    # Select the last run of the Actor that finished with a SUCCEEDED status
    last_succeeded_run_client = actor_client.last_run(status='SUCCEEDED')  # type: ignore[arg-type]

    # Get dataset
    actor_run_dataset_client = last_succeeded_run_client.dataset()

    # Fetch items from the run's dataset
    dataset_items = actor_run_dataset_client.list_items().items
