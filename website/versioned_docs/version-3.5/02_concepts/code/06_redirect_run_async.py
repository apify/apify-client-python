from apify_client import ApifyClientAsync

TOKEN = 'MY-APIFY-TOKEN'


async def main() -> None:
    apify_client = ApifyClientAsync(TOKEN)
    actor_client = apify_client.actor('username/actor-name')

    actor_run = await actor_client.start()
    run_client = apify_client.run(actor_run.id)

    # Use the helpers as context managers to redirect while the run is in progress.
    streamed_log = await run_client.get_streamed_log()
    status_message_watcher = await run_client.get_status_message_watcher()
    async with streamed_log, status_message_watcher:
        await run_client.wait_for_finish()

    # Or start and stop them yourself.
    actor_run = await actor_client.start()
    run_client = apify_client.run(actor_run.id)

    # With `from_start=False`, only log lines written from now on are redirected.
    streamed_log = await run_client.get_streamed_log(from_start=False)
    streamed_log.start()
    # Do other work while the run's log is redirected.
    await streamed_log.stop()
