import asyncio
from datetime import timedelta

from apify_client import ApifyClientAsync

TOKEN = 'MY-APIFY-TOKEN'


async def main() -> None:
    # Client initialization with the API token
    apify_client = ApifyClientAsync(token=TOKEN)

    # Get the Actor client
    actor_client = apify_client.actor('apify/instagram-hashtag-scraper')

    input_data = {'hashtags': ['rainbow'], 'resultsLimit': 20}

    # Run the Actor and wait up to 60 seconds for it to finish.
    # Input is not persisted for next runs.
    run_result = await actor_client.call(
        run_input=input_data, wait_duration=timedelta(seconds=60)
    )


if __name__ == '__main__':
    asyncio.run(main())
