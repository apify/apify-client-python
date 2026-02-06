from apify_client import ApifyClientAsync

TOKEN = 'MY-APIFY-TOKEN'


async def main() -> None:
    apify_client = ApifyClientAsync(TOKEN)

    # Initialize the dataset client
    dataset_client = apify_client.dataset('dataset-id')

    # Define the pagination parameters
    limit = 1000  # Number of items per page
    offset = 0  # Starting offset
    all_items = []  # List to store all fetched items

    while True:
        # Fetch a page of items
        response = await dataset_client.list_items(limit=limit, offset=offset)
        items = response.items
        total = response.total

        print(f'Fetched {len(items)} items')

        # Add the fetched items to the complete list
        all_items.extend(items)

        # Exit the loop if there are no more items to fetch
        if offset + limit >= total:
            break

        # Increment the offset for the next page
        offset += limit

    print(f'Overall fetched {len(all_items)} items')
