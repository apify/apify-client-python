from apify_client import ApifyClientAsync

TOKEN = 'MY-APIFY-TOKEN'


async def main() -> None:
    apify_client = ApifyClientAsync(TOKEN)
    run_client = apify_client.run('MY-RUN-ID')
    log_client = run_client.log()

    async with log_client.stream() as log_stream:
        if log_stream:
            for line in log_stream.iter_lines():
                print(line)
