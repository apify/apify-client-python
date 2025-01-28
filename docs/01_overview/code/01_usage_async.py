from apify_client import ApifyClientAsync

# You can find your API token at https://console.apify.com/settings/integrations.
TOKEN = 'MY-APIFY-TOKEN'


async def main() -> None:
    apify_client = ApifyClientAsync(TOKEN)

    # Start an Actor and wait for it to finish.
    actor_client = apify_client.actor('john-doe/my-cool-actor')
    call_result = await actor_client.call()

    if call_result is None:
        print('Actor run failed.')
        return

    # Fetch results from the Actor run's default dataset.
    dataset_client = apify_client.dataset(call_result['defaultDatasetId'])
    list_items_result = await dataset_client.list_items()
    print(f'Dataset: {list_items_result}')
