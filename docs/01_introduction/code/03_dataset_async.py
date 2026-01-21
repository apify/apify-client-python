from apify_client import ApifyClientAsync

TOKEN = 'MY-APIFY-TOKEN'


async def main() -> None:
    apify_client = ApifyClientAsync(TOKEN)
    dataset_client = apify_client.dataset('dataset-id')

    # Lists items from the Actor's dataset.
    dataset_items = (await dataset_client.list_items()).items
