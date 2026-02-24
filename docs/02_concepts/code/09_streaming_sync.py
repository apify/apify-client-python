from apify_client import ApifyClient

TOKEN = 'MY-APIFY-TOKEN'


def main() -> None:
    apify_client = ApifyClient(token=TOKEN)
    run_client = apify_client.run(run_id='MY-RUN-ID')
    log_client = run_client.log()

    with log_client.stream() as log_stream:
        if log_stream:
            for bytes_chunk in log_stream.iter_bytes():
                print(bytes_chunk)
