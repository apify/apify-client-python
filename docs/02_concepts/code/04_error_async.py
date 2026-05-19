import asyncio

from apify_client import ApifyClientAsync
from apify_client.errors import ApifyApiError, NotFoundError

TOKEN = 'MY-APIFY-TOKEN'


async def main() -> None:
    apify_client = ApifyClientAsync(TOKEN)

    try:
        # Try to list items from a non-existing dataset.
        dataset_client = apify_client.dataset('non-existing-dataset-id')
        dataset_items = (await dataset_client.list_items()).items
    except NotFoundError:
        # 404 — branch on a specific subclass when you want to react to it.
        dataset_items = []
    except ApifyApiError as err:
        # Catch-all for every other API error.
        print(f'API error: {err}')
        dataset_items = []

    print(f'Fetched {len(dataset_items)} items.')


if __name__ == '__main__':
    asyncio.run(main())
