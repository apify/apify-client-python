from apify_client import ApifyClientAsync

TOKEN = 'MY-APIFY-TOKEN'


async def main() -> None:
    apify_client = ApifyClientAsync(TOKEN)
    dataset_client = apify_client.dataset('dataset-id')

    # Define the pagination parameters
    limit = 1500  # Number of items in total
    offset = 100  # Starting offset

    # Iterate through items automatically, lazily sending as many API calls
    # as needed and receiving items in chunks.
    async for item in dataset_client.iterate_items(limit=limit, offset=offset):
        print(item)  # Process the item as needed
