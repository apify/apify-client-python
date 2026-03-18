import pandas as pd

from apify_client import ApifyClient

TOKEN = 'MY-APIFY-TOKEN'


def main() -> None:
    # Initialize the Apify client
    apify_client = ApifyClient(token=TOKEN)
    actor_client = apify_client.actor('apify/web-scraper')
    run_client = actor_client.last_run()
    dataset_client = run_client.dataset()

    # Load items from last dataset run
    dataset_data = dataset_client.list_items()

    # Pass dataset items to Pandas DataFrame
    data_frame = pd.DataFrame(dataset_data.items)

    print(data_frame.info)


if __name__ == '__main__':
    main()
