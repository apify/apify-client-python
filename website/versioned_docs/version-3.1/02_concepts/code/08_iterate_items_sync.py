from apify_client import ApifyClient

TOKEN = 'MY-APIFY-TOKEN'


def main() -> None:
    apify_client = ApifyClient(TOKEN)
    dataset_client = apify_client.dataset('dataset-id')

    # Define the pagination parameters
    limit = 1500  # Number of items in total
    offset = 100  # Starting offset

    # Iterate through items automatically, lazily sending as many API calls
    # as needed and receiving items in chunks.
    for item in dataset_client.iterate_items(limit=limit, offset=offset):
        print(item)  # Process the item as needed


if __name__ == '__main__':
    main()
