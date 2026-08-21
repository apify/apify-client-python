from apify_client import ApifyClient
from apify_client.http_clients import HttpxHttpClient


def main() -> None:
    with HttpxHttpClient() as http_client:
        client = ApifyClient.with_custom_http_client(
            token='MY-APIFY-TOKEN',
            http_client=http_client,
        )
        print(client.actor('apify/hello-world').get())
