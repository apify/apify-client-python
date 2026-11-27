from datetime import datetime, timedelta

from apify_client import ApifyClient

TOKEN = 'MY-APIFY-TOKEN'
RECORD_KEY = 'LOG_REDIRECTED_UNTIL'


def main() -> None:
    apify_client = ApifyClient(TOKEN)
    run_client = apify_client.run('MY-RUN-ID')
    store_client = apify_client.key_value_store('MY-STORE-ID')

    # After a reboot, continue after the last line redirected before it.
    record = store_client.get_record(RECORD_KEY)
    since = None
    if record:
        since = datetime.fromisoformat(record['value']) + timedelta(milliseconds=1)

    streamed_log = run_client.get_streamed_log(since=since)
    with streamed_log:
        run_client.wait_for_finish()

    # Before a reboot, save how far the redirection got. Here it is saved once the
    # run finishes; save it on your own reboot or migration signal instead.
    if streamed_log.last_redirected_at:
        redirected_until = streamed_log.last_redirected_at.isoformat()
        store_client.set_record(RECORD_KEY, redirected_until)
