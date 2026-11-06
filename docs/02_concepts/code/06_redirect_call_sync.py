import logging

from apify_client import ApifyClient

TOKEN = 'MY-APIFY-TOKEN'


def main() -> None:
    apify_client = ApifyClient(TOKEN)
    actor_client = apify_client.actor('username/actor-name')

    # By default, the run's log and status messages go to a built-in redirect logger.
    actor_client.call()

    # Send the run's log and status messages to your own logger.
    logging.basicConfig(level=logging.INFO)
    my_logger = logging.getLogger('my_actor_run')
    actor_client.call(logger=my_logger)

    # Turn the redirection off.
    actor_client.call(logger=None)
