from apify_client import ApifyClient

TOKEN = 'MY-APIFY-TOKEN'


def main() -> None:
    apify_client = ApifyClient(TOKEN)

    # Initialize the dataset client
    dataset_client = apify_client.dataset('dataset-id')

    # Define the pagination parameters
    limit = 1000  # Number items to request from API
    offset = 0  # Starting offset

    # Send single API call to fetch paginated items.
    # (number of items per single call can be limited by API)
    paginated_items = dataset_client.list_items(limit=limit, offset=offset)

    # Inspect pagination metadata returned by API
    print(paginated_items.total)

    for item in paginated_items.items:
        print(item)  # Process the item as needed
