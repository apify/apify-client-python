import asyncio

from apify_client import ApifyClientAsync
from apify_client.http_clients import Httpx2HttpClientAsync

TOKEN = 'MY-APIFY-TOKEN'


async def main() -> None:
    async with Httpx2HttpClientAsync() as http_client:
        client = ApifyClientAsync.with_custom_http_client(
            token=TOKEN,
            http_client=http_client,
        )
        print(await client.actor('apify/hello-world').get())


if __name__ == '__main__':
    asyncio.run(main())
