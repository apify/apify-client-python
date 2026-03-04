from __future__ import annotations

from typing import TYPE_CHECKING, Any

import httpx

from apify_client import ApifyClient, HttpClient, HttpResponse

if TYPE_CHECKING:
    from datetime import timedelta

TOKEN = 'MY-APIFY-TOKEN'


class HttpxClient(HttpClient):
    """Custom HTTP client using HTTPX library."""

    def __init__(self) -> None:
        super().__init__()
        self._client = httpx.Client()

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
        timeout: timedelta | None = None,
    ) -> HttpResponse:
        timeout_secs = timeout.total_seconds() if timeout else 0

        # httpx.Response satisfies the HttpResponse protocol,
        # so it can be returned directly.
        return self._client.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            content=data,
            json=json,
            timeout=timeout_secs,
        )


def main() -> None:
    client = ApifyClient.with_custom_http_client(
        token=TOKEN,
        http_client=HttpxClient(),
    )

    actor = client.actor('apify/hello-world').get()
    print(actor)


if __name__ == '__main__':
    main()
