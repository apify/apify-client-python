from datetime import timedelta

from apify_client import ApifyClientAsync

TOKEN = 'MY-APIFY-TOKEN'


async def main() -> None:
    apify_client = ApifyClientAsync(
        token=TOKEN,
        max_retries=4,
        min_delay_between_retries=timedelta(milliseconds=500),
        timeout_short=timedelta(seconds=5),
        timeout_medium=timedelta(seconds=30),
        timeout_long=timedelta(seconds=360),
        timeout_max=timedelta(seconds=360),
    )
