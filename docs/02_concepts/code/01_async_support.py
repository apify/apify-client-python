import asyncio

from apify_client import ApifyClientAsync

TOKEN = 'MY-APIFY-TOKEN'


async def main() -> None:
    apify_client = ApifyClientAsync(TOKEN)
    actor_client = apify_client.actor('my-actor-id')

    # Start the Actor and get the run ID
    run_result = await actor_client.start()
    run_client = apify_client.run(run_result['id'])
    log_client = run_client.log()

    # Stream the logs
    async with log_client.stream() as async_log_stream:
        if async_log_stream:
            async for line in async_log_stream.aiter_lines():
                print(line)


if __name__ == '__main__':
    asyncio.run(main())
