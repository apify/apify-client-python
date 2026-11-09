from datetime import timedelta

from apify_client import ApifyClient

TOKEN = 'MY-APIFY-TOKEN'


def main() -> None:
    # Configure default timeout tiers globally.
    apify_client = ApifyClient(
        token=TOKEN,
        timeout_short=timedelta(seconds=10),
        timeout_medium=timedelta(seconds=60),
        timeout_long=timedelta(seconds=600),
        timeout_max=timedelta(seconds=600),
    )

    dataset_client = apify_client.dataset('dataset-id')

    # Override the timeout for a single call using a timedelta.
    items = dataset_client.list_items(timeout=timedelta(seconds=120))

    # Or use a tier literal to select a predefined timeout.
    items = dataset_client.list_items(timeout='long')
