from apify_client import ApifyClientAsync

TOKEN = 'MY-APIFY-TOKEN'


async def main() -> None:
    apify_client = ApifyClientAsync(token=TOKEN)
    run_client = apify_client.run(run_id='MY-RUN-ID')
    log_client = run_client.log()

    async with log_client.stream() as log_stream:
        if log_stream:
            async for bytes_chunk in log_stream.aiter_bytes():
                print(bytes_chunk)
