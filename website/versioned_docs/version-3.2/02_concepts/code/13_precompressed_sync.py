import gzip
from pathlib import Path

from apify_client import ApifyClient

TOKEN = 'MY-APIFY-TOKEN'


def main() -> None:
    apify_client = ApifyClient(TOKEN)
    kvs_client = apify_client.key_value_store('MY-KVS-ID')

    report = Path('report.csv').read_bytes()
    compressed_report = gzip.compress(report)

    # The explicit content encoding stops the client from compressing the bytes again.
    kvs_client.set_record(
        'report',
        compressed_report,
        content_type='text/csv',
        content_encoding='gzip',
    )
