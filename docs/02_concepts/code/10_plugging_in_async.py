from typing_extensions import override

from apify_client import ApifyClientAsync
from apify_client.http_clients import HttpClientAsync, HttpResponse

TOKEN = 'MY-APIFY-TOKEN'


class MyHttpClientAsync(HttpClientAsync):
    """Custom async HTTP client."""

    @override
    async def send_request(
        self,
        *,
        method: str,
        url: str,
        headers: dict[str, str],
        content: bytes | None,
        timeout: float | None,
        stream: bool,
    ) -> HttpResponse:
        """Send one request through the custom transport."""
        raise NotImplementedError

    @override
    def is_retryable_transport_error(self, exc: Exception) -> bool:
        # List the transport's transient failures here, e.g. its timeout
        # and connection errors. Returning False for everything opts out
        # of transport retries entirely.
        return isinstance(exc, TimeoutError)


async def main() -> None:
    client = ApifyClientAsync.with_custom_http_client(
        token=TOKEN,
        http_client=MyHttpClientAsync(),
    )
