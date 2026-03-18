from apify_client import ApifyClient

TOKEN = 'MY-APIFY-TOKEN'


def main() -> None:
    apify_client = ApifyClient(TOKEN)
    run_client = apify_client.run('MY-RUN-ID')
    log_client = run_client.log()

    with log_client.stream() as log_stream:
        if log_stream:
            for line in log_stream.iter_lines():
                print(line)
