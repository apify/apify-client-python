from apify_client import ApifyClient

TOKEN = 'MY-APIFY-TOKEN'


def main() -> None:
    apify_client = ApifyClient(token=TOKEN)

    try:
        # Try to list items from non-existing dataset
        dataset_client = apify_client.dataset(dataset_id='not-existing-dataset-id')
        dataset_items = dataset_client.list_items().items
    except Exception as ApifyApiError:
        # The exception is an instance of ApifyApiError
        print(ApifyApiError)
