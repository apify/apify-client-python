from datetime import timedelta

from apify_client import ApifyClientAsync

TOKEN = 'MY-APIFY-TOKEN'


async def main() -> None:
    apify_client = ApifyClientAsync(
        token=TOKEN,
        max_retries=8,
        min_delay_between_retries=timedelta(milliseconds=500),  # 0.5s
        timeout=timedelta(seconds=360),  # 6 mins
    )
