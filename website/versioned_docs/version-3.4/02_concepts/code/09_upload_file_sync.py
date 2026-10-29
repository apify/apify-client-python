from pathlib import Path

from apify_client import ApifyClient

TOKEN = 'MY-APIFY-TOKEN'


def main() -> None:
    apify_client = ApifyClient(TOKEN)
    kvs_client = apify_client.key_value_store('MY-KVS-ID')

    # The file is read in chunks as it uploads, so its size doesn't matter.
    with Path('backup.tar.gz').open('rb') as backup:
        kvs_client.set_record('backup.tar.gz', backup, content_type='application/gzip')
