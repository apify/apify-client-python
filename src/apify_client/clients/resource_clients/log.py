import io
from typing import Any, Optional, cast

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

    def stream(self) -> Optional[io.IOBase]:
        """Retrieve the log as a file-like object.

        https://docs.apify.com/api/v2#/reference/logs/log/get-log

        Returns:
            io.IOBase, optional: The retrieved log as a file-like object, or None, if it does not exist.
        """
        try:
            response = self.http_client.call(
                url=self.url,
                method='GET',
                params=self._params(),
                stream=True,
                parse_response=False,
            )

            response.raw.decode_content = True
            # TODO explain response.raw.close()
            # response.raw is the raw urllib3 response, which subclasses IOBase
            return cast(io.IOBase, response.raw)

        except ApifyApiError as exc:
            _catch_not_found_or_throw(exc)

        return None
