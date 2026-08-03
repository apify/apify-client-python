import asyncio
from pathlib import Path

from apify_client import ApifyClientAsync

TOKEN = 'MY-APIFY-TOKEN'


async def main() -> None:
    apify_client = ApifyClientAsync(TOKEN)
    kvs_client = apify_client.key_value_store('MY-KVS-ID')

    screenshot = await asyncio.to_thread(Path('screenshot.png').read_bytes)

    # The explicit content type lets the client skip compressing the PNG.
    await kvs_client.set_record('screenshot', screenshot, content_type='image/png')
