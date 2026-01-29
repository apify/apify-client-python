from __future__ import annotations

import gzip
import json as jsonlib
import os
import sys
from datetime import datetime, timezone
from importlib import metadata
from typing import TYPE_CHECKING, Any
from urllib.parse import urlencode

import impit

from apify_client._statistics import ClientStatistics
from apify_client.errors import InvalidResponseBodyError

if TYPE_CHECKING:
    from apify_client._config import ClientConfig
    from apify_client._consts import JsonSerializable


class BaseHttpClient:
    """Base class for HTTP clients with shared configuration and utilities.

    Subclasses should call `super().__init__()` and create their specific impit client using the `_headers` attribute.
    """

    def __init__(self, config: ClientConfig, statistics: ClientStatistics | None = None) -> None:
        """Initialize the base HTTP client.

        Args:
            config: Client configuration with API URL, token, timeout, and retry settings.
            statistics: Statistics tracker for API calls. Created automatically if not provided.
        """
        self._config = config
        self._statistics = statistics or ClientStatistics()

        # Build headers for subclasses to use when creating their impit clients.
        headers: dict[str, str] = {'Accept': 'application/json, */*'}

        workflow_key = os.getenv('APIFY_WORKFLOW_KEY')
        if workflow_key is not None:
            headers['X-Apify-Workflow-Key'] = workflow_key

        is_at_home = 'APIFY_IS_AT_HOME' in os.environ
        python_version = '.'.join([str(x) for x in sys.version_info[:3]])
        client_version = metadata.version('apify-client')

        user_agent = f'ApifyClient/{client_version} ({sys.platform}; Python/{python_version}); isAtHome/{is_at_home}'
        headers['User-Agent'] = user_agent

        if config.token is not None:
            headers['Authorization'] = f'Bearer {config.token}'

        self._headers = headers

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
                utc_aware_dt = value.astimezone(timezone.utc)
                iso_str = utc_aware_dt.isoformat(timespec='milliseconds')
                parsed_params[key] = iso_str.replace('+00:00', 'Z')
            elif value is not None:
                parsed_params[key] = value

        return parsed_params

    @staticmethod
    def _is_retryable_error(exc: Exception) -> bool:
        """Check if an exception represents a transient error that should be retried."""
        return isinstance(
            exc,
            (
                InvalidResponseBodyError,
                impit.NetworkError,
                impit.TimeoutException,
                impit.RemoteProtocolError,
            ),
        )

    def _prepare_request_call(
        self,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        data: Any = None,
        json: JsonSerializable | None = None,
    ) -> tuple[dict[str, str], dict[str, Any] | None, Any]:
        """Prepare headers, params, and body for an HTTP request. Serializes JSON and applies gzip compression."""
        if json and data:
            raise ValueError('Cannot pass both "json" and "data" parameters at the same time!')

        if not headers:
            headers = {}

        # Dump JSON data to string so it can be gzipped.
        if json:
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

    def _calculate_timeout(self, attempt: int, timeout_secs: int | None = None) -> int:
        """Calculate timeout for a request attempt with exponential increase, bounded by client timeout."""
        return min(self._config.timeout_secs, (timeout_secs or self._config.timeout_secs) * 2 ** (attempt - 1))
