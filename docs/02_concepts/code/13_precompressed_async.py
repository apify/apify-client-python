import asyncio
import gzip
from pathlib import Path

from apify_client import ApifyClientAsync

TOKEN = 'MY-APIFY-TOKEN'


async def main() -> None:
    apify_client = ApifyClientAsync(TOKEN)
    kvs_client = apify_client.key_value_store('MY-KVS-ID')

    report = await asyncio.to_thread(Path('report.csv').read_bytes)
    compressed_report = await asyncio.to_thread(gzip.compress, report)

    # The explicit content encoding stops the client from compressing the bytes again.
    await kvs_client.set_record(
        'report',
        compressed_report,
        content_type='text/csv',
        content_encoding='gzip',
    )


if __name__ == '__main__':
    asyncio.run(main())
