from apify_client import ApifyClient

TOKEN = 'MY-APIFY-TOKEN'


def main() -> None:
    apify_client = ApifyClient(TOKEN)
    dataset_client = apify_client.dataset('dataset-id')

    # Iterate through all items automatically.
    for item in dataset_client.iterate_items():
        print(item)


if __name__ == '__main__':
    main()
