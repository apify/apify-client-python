from typing import Any

from apify_client import ApifyClient, HttpClient, HttpResponse, Timeout

TOKEN = 'MY-APIFY-TOKEN'


class MyHttpClient(HttpClient):
    """Custom sync HTTP client."""

    def call(
        self,
        *,
        method: str,
        url: str,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        data: str | bytes | bytearray | None = None,
        json: Any = None,
        stream: bool | None = None,
        timeout: Timeout = 'medium',
    ) -> HttpResponse: ...


def main() -> None:
    client = ApifyClient.with_custom_http_client(
        token=TOKEN,
        http_client=MyHttpClient(),
    )
