from typing import Any

from apify_client import ApifyClientAsync, HttpClientAsync, HttpResponse, Timeout

TOKEN = 'MY-APIFY-TOKEN'


class MyHttpClientAsync(HttpClientAsync):
    """Custom async HTTP client."""

    async def call(
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


async def main() -> None:
    client = ApifyClientAsync.with_custom_http_client(
        token=TOKEN,
        http_client=MyHttpClientAsync(),
    )
