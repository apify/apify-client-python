import aiofiles

from apify_client import ApifyClientAsync

TOKEN = 'MY-APIFY-TOKEN'


async def main() -> None:
    apify_client = ApifyClientAsync(TOKEN)
    kvs_client = apify_client.key_value_store('MY-KVS-ID')

    # The file is read in chunks as it uploads, so its size doesn't matter.
    async with aiofiles.open('backup.tar.gz', 'rb') as backup:
        await kvs_client.set_record(
            'backup.tar.gz', backup, content_type='application/gzip'
        )
