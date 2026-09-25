import asyncio
from pathlib import Path

from apify_client import ApifyClientAsync

TOKEN = 'MY-APIFY-TOKEN'


async def main() -> None:
    apify_client = ApifyClientAsync(TOKEN)
    kvs_client = apify_client.key_value_store('MY-KVS-ID')

    # The file is read in chunks in a worker thread as it uploads, so its size
    # doesn't matter.
    backup = await asyncio.to_thread(Path('backup.tar.gz').open, 'rb')
    with backup:
        await kvs_client.set_record(
            'backup.tar.gz', backup, content_type='application/gzip'
        )
