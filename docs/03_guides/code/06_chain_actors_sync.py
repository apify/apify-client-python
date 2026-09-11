from apify_client import ApifyClient

TOKEN = 'MY-APIFY-TOKEN'


def main() -> None:
    apify_client = ApifyClient(token=TOKEN)

    # Run the first Actor and wait for it to finish.
    producer_run = apify_client.actor('my-org/producer-actor').call(
        run_input={'startUrls': [{'url': 'https://example.com'}]},
    )
    if producer_run is None:
        raise RuntimeError('The producer run was not found')

    # Stream the producer's OUTPUT record straight into the consumer's input.
    # The record uploads as it downloads, so it never has to fit in memory.
    producer_store = apify_client.key_value_store(producer_run.default_key_value_store_id)
    with producer_store.stream_record('OUTPUT') as record:
        if record is None:
            raise RuntimeError('The producer stored no OUTPUT record')
        consumer_run = apify_client.actor('my-org/consumer-actor').call(
            run_input=record['value'],
            content_type=record['content_type'],
        )
    print(consumer_run)

    # Export the producer's dataset as CSV into a named key-value store, where
    # the next stage of the pipeline can pick it up as a single file.
    reports_store = apify_client.key_value_stores().get_or_create(name='pipeline-reports')
    reports_client = apify_client.key_value_store(reports_store.id)
    producer_dataset = apify_client.dataset(producer_run.default_dataset_id)
    with producer_dataset.stream_items(item_format='csv') as items:
        reports_client.set_record('items.csv', items, content_type='text/csv')


if __name__ == '__main__':
    main()
