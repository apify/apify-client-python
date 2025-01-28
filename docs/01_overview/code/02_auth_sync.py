from apify_client import ApifyClient

TOKEN = 'MY-APIFY-TOKEN'


def main() -> None:
    # Client initialization with the API token.
    apify_client = ApifyClient(TOKEN)
