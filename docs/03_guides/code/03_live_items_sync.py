from apify_client import ApifyClient

TOKEN = 'MY-APIFY-TOKEN'


def main() -> None:
    apify_client = ApifyClient(TOKEN)

    # Start the Actor without waiting for it to finish
    actor_client = apify_client.actor('username/actor-name')
    run = actor_client.start(run_input={'query': 'web scraping'})

    # Each item arrives shortly after the run pushes it. The loop ends once the run
    # has finished and every item is read.
    for item in apify_client.run(run.id).iterate_dataset_items(skip_empty=True):
        print(item)


if __name__ == '__main__':
    main()
