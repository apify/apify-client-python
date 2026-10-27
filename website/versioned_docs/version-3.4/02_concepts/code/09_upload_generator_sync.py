from collections.abc import Iterator

from apify_client import ApifyClient

TOKEN = 'MY-APIFY-TOKEN'


def csv_chunks() -> Iterator[str]:
    """Build the CSV in pieces, for example from pages of a database query."""
    yield 'id,value\n'
    for start in range(0, 1_000_000, 10_000):
        yield ''.join(f'{i},{i * i}\n' for i in range(start, start + 10_000))


def main() -> None:
    apify_client = ApifyClient(TOKEN)
    kvs_client = apify_client.key_value_store('MY-KVS-ID')

    # Each chunk is encoded and sent as it's produced. An iterator can't be
    # rewound, so a failed upload isn't retried.
    kvs_client.set_record('report.csv', csv_chunks(), content_type='text/csv')
