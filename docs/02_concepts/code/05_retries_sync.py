from apify_client import ApifyClient

TOKEN = 'MY-APIFY-TOKEN'


async def main() -> None:
    apify_client = ApifyClient(
        token=TOKEN,
        max_retries=8,
        min_delay_between_retries_millis=500,  # 0.5s
        timeout_secs=360,  # 6 mins
    )
