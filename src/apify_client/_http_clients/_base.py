from __future__ import annotations

import gzip
import json as jsonlib
import os
import sys
from abc import ABC, abstractmethod
from datetime import UTC, datetime, timedelta
from importlib import metadata
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable
from urllib.parse import urlencode

from apify_client._consts import DEFAULT_MAX_RETRIES, DEFAULT_MIN_DELAY_BETWEEN_RETRIES, DEFAULT_TIMEOUT
from apify_client._docs import docs_group
from apify_client._statistics import ClientStatistics
from apify_client._utils import to_seconds

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator, Mapping

    from apify_client._consts import JsonSerializable


@docs_group('HTTP clients')
@runtime_checkable
class HttpResponse(Protocol):
    """Protocol for HTTP response objects returned by HTTP clients.

    Any object that has the required attributes and methods can be used as an HTTP response
    (e.g., `impit.Response`). This enables custom HTTP client implementations to return
    their own response types.
    """

    @property
    def status_code(self) -> int:
        """HTTP status code of the response."""

    @property
    def text(self) -> str:
        """Response body decoded as text."""

    @property
    def content(self) -> bytes:
        """Raw response body as bytes."""

    @property
    def headers(self) -> Mapping[str, str]:
        """Response headers as a mapping."""

    def json(self) -> Any:
        """Parse response body as JSON."""

    def read(self) -> bytes:
        """Read the entire response body."""

    async def aread(self) -> bytes:
        """Read the entire response body asynchronously."""

    def close(self) -> None:
        """Close the response and release the connection."""

    async def aclose(self) -> None:
        """Close the response and release the connection asynchronously."""

    def iter_bytes(self) -> Iterator[bytes]:
        """Iterate over the response body in bytes chunks."""

    def aiter_bytes(self) -> AsyncIterator[bytes]:
        """Iterate over the response body in bytes chunks asynchronously."""


@docs_group('HTTP clients')
class HttpClientBase:
    """Shared configuration and utilities for HTTP clients.

    Provides common functionality for both sync and async HTTP clients including:
    header construction, parameter parsing, request body preparation, URL building,
    and timeout calculation.

    Subclasses should call `super().__init__()` to initialize shared configuration.
    The helper methods are then available for use in the `call()` implementation.
    """

    def __init__(
        self,
        *,
        token: str | None = None,
        timeout: timedelta = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        min_delay_between_retries: timedelta = DEFAULT_MIN_DELAY_BETWEEN_RETRIES,
        statistics: ClientStatistics | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        """Initialize the HTTP client base.

        Args:
            token: Apify API token for authentication.
            timeout: Request timeout.
            max_retries: Maximum number of retries for failed requests.
            min_delay_between_retries: Minimum delay between retries.
            statistics: Statistics tracker for API calls. Created automatically if not provided.
            headers: Additional HTTP headers to include in all requests.
        """
        self._timeout = timeout
        self._max_retries = max_retries
        self._min_delay_between_retries = min_delay_between_retries
        self._statistics = statistics or ClientStatistics()

        # Build default headers.
        default_headers: dict[str, str] = {'Accept': 'application/json, */*'}

        workflow_key = os.getenv('APIFY_WORKFLOW_KEY')
        if workflow_key is not None:
            default_headers['X-Apify-Workflow-Key'] = workflow_key

        is_at_home = 'APIFY_IS_AT_HOME' in os.environ
        python_version = '.'.join([str(x) for x in sys.version_info[:3]])
        client_version = metadata.version('apify-client')

        user_agent = f'ApifyClient/{client_version} ({sys.platform}; Python/{python_version}); isAtHome/{is_at_home}'
        default_headers['User-Agent'] = user_agent

        if token is not None:
            default_headers['Authorization'] = f'Bearer {token}'

        self._headers = {**default_headers, **(headers or {})}

    @staticmethod
    def _parse_params(params: dict[str, Any] | None) -> dict[str, Any] | None:
        """Convert request parameters to Apify API-compatible formats.

        Converts booleans to 0/1, lists to comma-separated strings, datetimes to ISO 8601 Zulu format.
        """
        if params is None:
            return None

        parsed_params: dict[str, Any] = {}
        for key, value in params.items():
            if isinstance(value, bool):
                parsed_params[key] = int(value)
            elif isinstance(value, list):
                parsed_params[key] = ','.join(value)
            elif isinstance(value, datetime):
                utc_aware_dt = value.astimezone(UTC)
                iso_str = utc_aware_dt.isoformat(timespec='milliseconds')
                parsed_params[key] = iso_str.replace('+00:00', 'Z')
            elif value is not None:
                parsed_params[key] = value

        return parsed_params

    def _prepare_request_call(
        self,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        data: str | bytes | bytearray | None = None,
        json: JsonSerializable | None = None,
    ) -> tuple[dict[str, str], dict[str, Any] | None, bytes | None]:
        """Prepare headers, params, and body for an HTTP request. Serializes JSON and applies gzip compression."""
        if json is not None and data is not None:
            raise ValueError('Cannot pass both "json" and "data" parameters at the same time!')

        if not headers:
            headers = {}

        # Dump JSON data to string so it can be gzipped.
        if json is not None:
            data = jsonlib.dumps(json, ensure_ascii=False, allow_nan=False, default=str).encode('utf-8')
            headers['Content-Type'] = 'application/json'

        if isinstance(data, (str, bytes, bytearray)):
            if isinstance(data, str):
                data = data.encode('utf-8')
            data = gzip.compress(data)
            headers['Content-Encoding'] = 'gzip'

        return (headers, self._parse_params(params), data)

    def _build_url_with_params(self, url: str, params: dict[str, Any] | None = None) -> str:
        """Build a URL with query parameters appended. List values are expanded into multiple key=value pairs."""
        if not params:
            return url

        param_pairs = list[tuple[str, str]]()
        for key, value in params.items():
            if isinstance(value, list):
                param_pairs.extend((key, str(v)) for v in value)
            else:
                param_pairs.append((key, str(value)))

        query_string = urlencode(param_pairs)

        return f'{url}?{query_string}'

    def _calculate_timeout(self, attempt: int, timeout: timedelta | None = None) -> float:
        """Calculate timeout for a request attempt with exponential increase, bounded by client timeout."""
        timeout_secs = to_seconds(timeout or self._timeout)
        client_timeout_secs = to_seconds(self._timeout)
        return min(client_timeout_secs, timeout_secs * 2 ** (attempt - 1))


@docs_group('HTTP clients')
class HttpClient(HttpClientBase, ABC):
    """Abstract base class for synchronous HTTP clients used by `ApifyClient`.

    Extend this class to create a custom synchronous HTTP client. Override the `call` method
    with your implementation. Helper methods from the base class are available for request
    preparation, URL building, and parameter parsing.
    """

    @abstractmethod
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
        """Make an HTTP request.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.).
            url: Full URL to make the request to.
            headers: Additional headers to include in this request.
            params: Query parameters to append to the URL.
            data: Raw request body data. Cannot be used together with json.
            json: JSON-serializable data for the request body. Cannot be used together with data.
            stream: Whether to stream the response body.
            timeout: Timeout for this specific request.

        Returns:
            The HTTP response object.

        Raises:
            ApifyApiError: If the request fails after all retries or returns a non-retryable error status.
            ValueError: If both json and data are provided.
        """
        ...


@docs_group('HTTP clients')
class HttpClientAsync(HttpClientBase, ABC):
    """Abstract base class for asynchronous HTTP clients used by `ApifyClientAsync`.

    Extend this class to create a custom asynchronous HTTP client. See `HttpClient`
    for details on the expected behavior.
    """

    @abstractmethod
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
        timeout: timedelta | None = None,
    ) -> HttpResponse:
        """Make an HTTP request.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.).
            url: Full URL to make the request to.
            headers: Additional headers to include in this request.
            params: Query parameters to append to the URL.
            data: Raw request body data. Cannot be used together with json.
            json: JSON-serializable data for the request body. Cannot be used together with data.
            stream: Whether to stream the response body.
            timeout: Timeout for this specific request.

        Returns:
            The HTTP response object.

        Raises:
            ApifyApiError: If the request fails after all retries or returns a non-retryable error status.
            ValueError: If both json and data are provided.
        """
        ...
