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
    """Base class for HTTP clients with shared configuration and utilities."""

    def __init__(self, config: ClientConfig, statistics: ClientStatistics | None = None) -> None:
        """Initialize HTTP client with configuration.

        Args:
            config: Immutable client configuration.
            statistics: Optional statistics tracker.
        """
        self._config = config
        self._statistics = statistics or ClientStatistics()

        # Build headers
        headers = {'Accept': 'application/json, */*'}

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

        # Create impit clients
        self.impit_client = impit.Client(
            headers=headers,
            follow_redirects=True,
            timeout=config.timeout_secs,
        )
        self.impit_async_client = impit.AsyncClient(
            headers=headers,
            follow_redirects=True,
            timeout=config.timeout_secs,
        )

    @staticmethod
    def _parse_params(params: dict | None) -> dict | None:
        if params is None:
            return None

        parsed_params: dict = {}
        for key, value in params.items():
            # Our API needs boolean parameters passed as 0 or 1
            if isinstance(value, bool):
                parsed_params[key] = int(value)
            # Our API needs lists passed as comma-separated strings
            elif isinstance(value, list):
                parsed_params[key] = ','.join(value)
            elif isinstance(value, datetime):
                utc_aware_dt = value.astimezone(timezone.utc)

                iso_str = utc_aware_dt.isoformat(timespec='milliseconds')

                # Convert to ISO 8601 string in Zulu format
                zulu_date_str = iso_str.replace('+00:00', 'Z')

                parsed_params[key] = zulu_date_str
            elif value is not None:
                parsed_params[key] = value

        return parsed_params

    @staticmethod
    def _is_retryable_error(exc: Exception) -> bool:
        """Check if an exception should be retried.

        Args:
            exc: The exception to check.

        Returns:
            True if the exception is retryable (network errors, timeouts, etc.).
        """
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
        headers: dict | None = None,
        params: dict | None = None,
        data: Any = None,
        json: JsonSerializable | None = None,
    ) -> tuple[dict, dict | None, Any]:
        if json and data:
            raise ValueError('Cannot pass both "json" and "data" parameters at the same time!')

        if not headers:
            headers = {}

        # dump JSON data to string, so they can be gzipped
        if json:
            data = jsonlib.dumps(json, ensure_ascii=False, allow_nan=False, default=str).encode('utf-8')
            headers['Content-Type'] = 'application/json'

        if isinstance(data, (str, bytes, bytearray)):
            if isinstance(data, str):
                data = data.encode('utf-8')
            data = gzip.compress(data)
            headers['Content-Encoding'] = 'gzip'

        return (
            headers,
            self._parse_params(params),
            data,
        )

    def _build_url_with_params(self, url: str, params: dict | None = None) -> str:
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
