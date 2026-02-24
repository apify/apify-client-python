from apify_client import ApifyClient

TOKEN = 'MY-APIFY-TOKEN'


def main() -> None:
    apify_client = ApifyClient(TOKEN)
    dataset_client = apify_client.dataset('dataset-id')

    # Lists items from the Actor's dataset.
    dataset_items = dataset_client.list_items().items
