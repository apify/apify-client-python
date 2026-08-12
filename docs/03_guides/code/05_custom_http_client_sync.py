from __future__ import annotations

import json as jsonlib
from typing import TYPE_CHECKING, Any

import requests
from typing_extensions import override

from apify_client import ApifyClient
from apify_client.http_clients import HttpClient, HttpResponse

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator, Mapping

TOKEN = 'MY-APIFY-TOKEN'


class RequestsResponse:
    """Adapt a requests response to the Apify client's HttpResponse protocol."""

    def __init__(self, response: requests.Response) -> None:
        self._response = response
        self._body: bytes | None = None

    @property
    def status_code(self) -> int:
        return self._response.status_code

    @property
    def headers(self) -> Mapping[str, str]:
        return self._response.headers

    @property
    def content(self) -> bytes:
        if self._body is None:
            raise RuntimeError(
                'The streamed response has not been read yet; use read() or iter_bytes()'
            )
        return self._body

    @property
    def text(self) -> str:
        encoding = self._response.encoding or 'utf-8'
        return self.content.decode(encoding, errors='replace')

    def json(self) -> Any:
        return jsonlib.loads(self.text)

    def read(self) -> bytes:
        if self._body is None:
            self._body = self._response.content
        return self._body

    async def aread(self) -> bytes:
        return self.read()

    def close(self) -> None:
        self._response.close()

    async def aclose(self) -> None:
        self.close()

    def iter_bytes(self) -> Iterator[bytes]:
        if self._body is not None:
            if self._body:
                yield self._body
            return
        yield from self._response.iter_content(64 * 1024)

    async def aiter_bytes(self) -> AsyncIterator[bytes]:
        for chunk in self.iter_bytes():
            yield chunk


class RequestsHttpClient(HttpClient):
    """Minimal custom synchronous HTTP client backed by requests."""

    @override
    def __init__(self) -> None:
        super().__init__()
        self._session = requests.Session()

    @override
    def is_timeout_error(self, exc: Exception) -> bool:
        return super().is_timeout_error(exc) or isinstance(exc, requests.Timeout)

    @override
    def close(self) -> None:
        self._session.close()

    @override
    def send_request(
        self,
        *,
        method: str,
        url: str,
        headers: dict[str, str],
        content: bytes | None,
        timeout: float | None,
        stream: bool,
    ) -> HttpResponse:
        response = self._session.request(
            method=method,
            url=url,
            headers=headers,
            data=content,
            timeout=timeout,
            stream=stream,
        )
        adapted_response = RequestsResponse(response)

        if not stream:
            adapted_response.read()

        return adapted_response

    @override
    def is_retryable_transport_error(self, exc: Exception) -> bool:
        return isinstance(
            exc,
            (
                requests.ConnectionError,
                requests.Timeout,
                requests.exceptions.ChunkedEncodingError,
            ),
        )


def main() -> None:
    with RequestsHttpClient() as http_client:
        client = ApifyClient.with_custom_http_client(
            token=TOKEN,
            http_client=http_client,
        )
        actor = client.actor('apify/hello-world').get()
        print(actor)


if __name__ == '__main__':
    main()
