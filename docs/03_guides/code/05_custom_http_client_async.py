from __future__ import annotations

import asyncio
import json as jsonlib
from typing import TYPE_CHECKING, Any

import aiohttp
from typing_extensions import override

from apify_client import ApifyClientAsync
from apify_client.http_clients import HttpClientAsync, HttpResponse

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator, Mapping

TOKEN = 'MY-APIFY-TOKEN'


class AiohttpResponse:
    """Adapt an aiohttp response to the Apify client's HttpResponse protocol."""

    def __init__(self, response: aiohttp.ClientResponse) -> None:
        self._response = response
        self._body: bytes | None = None

    @property
    def status_code(self) -> int:
        return self._response.status

    @property
    def headers(self) -> Mapping[str, str]:
        return self._response.headers

    @property
    def content(self) -> bytes:
        if self._body is None:
            raise RuntimeError(
                'The streamed response has not been read yet; '
                'use aread() or aiter_bytes()'
            )
        return self._body

    @property
    def text(self) -> str:
        encoding = self._response.charset or 'utf-8'
        return self.content.decode(encoding, errors='replace')

    def json(self) -> Any:
        return jsonlib.loads(self.text)

    def read(self) -> bytes:
        return self.content

    async def aread(self) -> bytes:
        if self._body is None:
            self._body = await self._response.read()
        return self._body

    def close(self) -> None:
        self._response.close()

    async def aclose(self) -> None:
        self._response.release()
        await self._response.wait_for_close()

    def iter_bytes(self) -> Iterator[bytes]:
        body = self.content
        if body:
            yield body

    async def aiter_bytes(self) -> AsyncIterator[bytes]:
        if self._body is not None:
            if self._body:
                yield self._body
            return
        async for chunk in self._response.content.iter_chunked(64 * 1024):
            yield chunk


class AiohttpHttpClient(HttpClientAsync):
    """Minimal custom asynchronous HTTP client backed by aiohttp."""

    @override
    def __init__(self) -> None:
        super().__init__()
        self._session = aiohttp.ClientSession()

    @override
    def is_timeout_error(self, exc: Exception) -> bool:
        return super().is_timeout_error(exc) or isinstance(
            exc, aiohttp.ServerTimeoutError
        )

    @override
    async def aclose(self) -> None:
        await self._session.close()

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
        response = await self._session.request(
            method=method,
            url=url,
            headers=headers,
            data=content,
            timeout=aiohttp.ClientTimeout(total=timeout),
        )
        adapted_response = AiohttpResponse(response)

        if not stream:
            await adapted_response.aread()

        return adapted_response

    @override
    def is_retryable_transport_error(self, exc: Exception) -> bool:
        return isinstance(exc, (TimeoutError, aiohttp.ClientError))


async def main() -> None:
    async with AiohttpHttpClient() as http_client:
        client = ApifyClientAsync.with_custom_http_client(
            token=TOKEN,
            http_client=http_client,
        )
        actor = await client.actor('apify/hello-world').get()
        print(actor)


if __name__ == '__main__':
    asyncio.run(main())
