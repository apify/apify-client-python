from pathlib import Path

from apify_client import ApifyClient

TOKEN = 'MY-APIFY-TOKEN'


def main() -> None:
    apify_client = ApifyClient(TOKEN)
    kvs_client = apify_client.key_value_store('MY-KVS-ID')

    screenshot = Path('screenshot.png').read_bytes()

    # The explicit content type lets the client skip compressing the PNG.
    kvs_client.set_record('screenshot', screenshot, content_type='image/png')
