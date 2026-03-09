from __future__ import annotations

import asyncio
from typing import Any

import httpx

from apify_client import ApifyClientAsync, HttpClientAsync, HttpResponse, Timeout

TOKEN = 'MY-APIFY-TOKEN'


class HttpxClientAsync(HttpClientAsync):
    """Custom async HTTP client using HTTPX library."""

    def __init__(self) -> None:
        super().__init__()
        self._client = httpx.AsyncClient()

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
    ) -> HttpResponse:
        timeout_secs = self._compute_timeout(timeout, attempt=1) or 0

        # httpx.Response satisfies the HttpResponse protocol,
        # so it can be returned directly.
        return await self._client.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            content=data,
            json=json,
            timeout=timeout_secs,
        )


async def main() -> None:
    client = ApifyClientAsync.with_custom_http_client(
        token=TOKEN,
        http_client=HttpxClientAsync(),
    )

    actor = await client.actor('apify/hello-world').get()
    print(actor)


if __name__ == '__main__':
    asyncio.run(main())
