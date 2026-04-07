from apify_client import ApifyClientAsync

TOKEN = 'MY-APIFY-TOKEN'


async def main() -> None:
    apify_client = ApifyClientAsync(TOKEN)
    dataset_client = apify_client.dataset('dataset-id')

    # Iterate through all items automatically.
    async for item in dataset_client.iterate_items():
        print(item)
