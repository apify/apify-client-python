from contextlib import contextmanager
from typing import Any, Iterator, Optional

import httpx

from ..._errors import ApifyApiError
from ..._utils import _catch_not_found_or_throw
from ..base import ResourceClient


class LogClient(ResourceClient):
    """Sub-client for manipulating logs."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the LogClient."""
        resource_path = kwargs.pop('resource_path', 'logs')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def get(self) -> Optional[str]:
        """Retrieve the log as text.

        https://docs.apify.com/api/v2#/reference/logs/log/get-log

        Returns:
            str, optional: The retrieved log, or None, if it does not exist.
        """
        try:
            response = self.http_client.call(
                url=self.url,
                method='GET',
                params=self._params(),
            )

            return response.text

        except ApifyApiError as exc:
            _catch_not_found_or_throw(exc)

        return None

    def get_as_bytes(self) -> Optional[bytes]:
        """Retrieve the log as raw bytes.

        https://docs.apify.com/api/v2#/reference/logs/log/get-log

        Returns:
            bytes, optional: The retrieved log as raw bytes, or None, if it does not exist.
        """
        try:
            response = self.http_client.call(
                url=self.url,
                method='GET',
                params=self._params(),
                parse_response=False,
            )

            return response.content

        except ApifyApiError as exc:
            _catch_not_found_or_throw(exc)

        return None

    @contextmanager
    def stream(self) -> Iterator[Optional[httpx.Response]]:
        """Retrieve the log as a stream.

        https://docs.apify.com/api/v2#/reference/logs/log/get-log

        Returns:
            httpx.Response, optional: The retrieved log as a context-managed streaming Response, or None, if it does not exist.
        """
        response = None
        try:
            response = self.http_client.call(
                url=self.url,
                method='GET',
                params=self._params(stream=True),
                stream=True,
                parse_response=False,
            )

            yield response
        except ApifyApiError as exc:
            _catch_not_found_or_throw(exc)
            yield None
        finally:
            if response:
                response.close()
