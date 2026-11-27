from datetime import UTC, datetime

from apify_client import ApifyClient

TOKEN = 'MY-APIFY-TOKEN'


def main() -> None:
    apify_client = ApifyClient(TOKEN)
    actor_client = apify_client.actor('username/actor-name')

    actor_run = actor_client.start()
    run_client = apify_client.run(actor_run.id)

    # Use the helpers as context managers to redirect while the run is in progress.
    streamed_log = run_client.get_streamed_log()
    status_message_watcher = run_client.get_status_message_watcher()
    with streamed_log, status_message_watcher:
        run_client.wait_for_finish()

    # Or start and stop them yourself.
    actor_run = actor_client.start()
    run_client = apify_client.run(actor_run.id)

    # With `since`, only log lines written at that time or later are redirected.
    streamed_log = run_client.get_streamed_log(since=datetime.now(tz=UTC))
    streamed_log.start()
    # Do other work while the run's log is redirected.
    streamed_log.stop()
