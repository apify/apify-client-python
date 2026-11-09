from datetime import timedelta

from apify_client import ApifyClientAsync

TOKEN = 'MY-APIFY-TOKEN'


async def main() -> None:
    apify_client = ApifyClientAsync(TOKEN)

    # Retry the start until the account has the resources for the run.
    run = await apify_client.actor('username/actor-name').call(wait_for_resources=True)

    # Stop retrying after 10 minutes and raise the last error.
    started_run = await apify_client.task('username~task-name').start(
        wait_for_resources=timedelta(minutes=10),
    )
