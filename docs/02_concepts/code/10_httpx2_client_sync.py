from apify_client import ApifyClient
from apify_client.http_clients import Httpx2HttpClient

TOKEN = 'MY-APIFY-TOKEN'


def main() -> None:
    with Httpx2HttpClient() as http_client:
        client = ApifyClient.with_custom_http_client(
            token=TOKEN,
            http_client=http_client,
        )
        print(client.actor('apify/hello-world').get())


if __name__ == '__main__':
    main()
