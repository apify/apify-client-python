import logging

from apify_client import ApifyClientAsync

TOKEN = 'MY-APIFY-TOKEN'


async def main() -> None:
    apify_client = ApifyClientAsync(TOKEN)
    actor_client = apify_client.actor('username/actor-name')

    # By default, the run's log and status messages go to a built-in redirect logger.
    await actor_client.call()

    # Send the run's log and status messages to your own logger.
    logging.basicConfig(level=logging.INFO)
    my_logger = logging.getLogger('my_actor_run')
    await actor_client.call(logger=my_logger)

    # Turn the redirection off.
    await actor_client.call(logger=None)
