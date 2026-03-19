from apify_client import ApifyClientAsync

TOKEN = 'MY-APIFY-TOKEN'


async def main() -> None:
    # Client initialization with the API token.
    apify_client = ApifyClientAsync(TOKEN)
