from apify_client import ApifyClient
from apify_client.errors import ApifyApiError

TOKEN = 'MY-APIFY-TOKEN'


def main() -> None:
    apify_client = ApifyClient(TOKEN)

    try:
        # Try to list items from a non-existing dataset.
        dataset_client = apify_client.dataset('non-existing-dataset-id')
        dataset_items = dataset_client.list_items().items
    except ApifyApiError as err:
        # The client raises ApifyApiError for API errors.
        print(f'API error: {err}')


if __name__ == '__main__':
    main()
