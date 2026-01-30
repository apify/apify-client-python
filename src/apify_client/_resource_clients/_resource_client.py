from __future__ import annotations

import asyncio
import time
from datetime import datetime, timedelta, timezone
from functools import cached_property
from typing import TYPE_CHECKING, Any
from urllib.parse import urlencode

from apify_client._consts import DEFAULT_WAIT_FOR_FINISH, DEFAULT_WAIT_WHEN_JOB_NOT_EXIST, ActorJobStatus
from apify_client._logging import WithLogDetailsClient
from apify_client._representations import to_seconds
from apify_client._utils import catch_not_found_or_throw, response_to_dict, to_safe_id
from apify_client.errors import ApifyApiError, ApifyClientError

if TYPE_CHECKING:
    from apify_client._client_registry import ClientRegistry, ClientRegistryAsync
    from apify_client._http_clients import AsyncHttpClient, SyncHttpClient


class ResourceClient(metaclass=WithLogDetailsClient):
    """Base class for synchronous resource clients.

    Provides URL building, parameter handling, and client creation utilities.
    All methods are synchronous and don't perform I/O operations.
    """

    def __init__(
        self,
        *,
        base_url: str,
        public_base_url: str,
        http_client: SyncHttpClient,
        resource_path: str,
        client_registry: ClientRegistry,
        resource_id: str | None = None,
        params: dict | None = None,
    ) -> None:
        """Initialize the resource client.

        Args:
            base_url: API base URL.
            public_base_url: Public CDN base URL.
            http_client: HTTP client for making requests.
            resource_path: Resource endpoint path (e.g., 'actors', 'datasets').
            client_registry: Bundle of client classes for dependency injection.
            resource_id: Optional resource ID for single-resource clients.
            params: Optional default parameters for all requests.
        """
        if resource_path.endswith('/'):
            raise ValueError('resource_path must not end with "/"')

        self._base_url = base_url
        self._public_base_url = public_base_url
        self._http_client = http_client
        self._default_params = params or {}
        self._resource_path = resource_path
        self._resource_id = resource_id
        self._client_registry = client_registry

    @property
    def resource_id(self) -> str | None:
        """Get the resource ID."""
        return self._resource_id

    @property
    def _resource_url(self) -> str:
        """Build the full resource URL from base URL, path, and optional ID."""
        url = f'{self._base_url}/{self._resource_path}'
        if self._resource_id is not None:
            url = f'{url}/{to_safe_id(self._resource_id)}'
        return url

    @cached_property
    def _base_client_kwargs(self) -> dict[str, Any]:
        """Base kwargs for creating nested/child clients.

        Returns dict with base_url, public_base_url, http_client, and client_registry. Caller adds
        resource_path, resource_id, and params as needed.
        """
        return {
            'base_url': self._resource_url,
            'public_base_url': self._public_base_url,
            'http_client': self._http_client,
            'client_registry': self._client_registry,
        }

    def _build_url(
        self,
        path: str | None = None,
        *,
        public: bool = False,
        params: dict | None = None,
    ) -> str:
        """Build complete URL for API request.

        Args:
            path: Optional path segment to append (e.g., 'runs', 'items').
            public: Whether to use public CDN URL instead of API URL.
            params: Optional query parameters to append.

        Returns:
            Complete URL with optional path and query string.
        """
        url = f'{self._resource_url}/{path}' if path else self._resource_url

        if public:
            if not url.startswith(self._base_url):
                raise ValueError(f'URL {url} does not start with base URL {self._base_url}')
            url = url.replace(self._base_url, self._public_base_url, 1)

        if params:
            filtered = {k: v for k, v in params.items() if v is not None}
            if filtered:
                separator = '&' if '?' in url else '?'
                url += separator + urlencode(filtered)

        return url

    def _build_params(self, **kwargs: Any) -> dict:
        """Merge default params with method params, filtering out None values.

        Args:
            **kwargs: Method-specific parameters to merge.

        Returns:
            Merged parameters with None values removed.
        """
        merged = {**self._default_params, **kwargs}
        return {k: v for k, v in merged.items() if v is not None}

    def _wait_for_finish(
        self,
        url: str,
        params: dict,
        wait_duration: timedelta | None = None,
    ) -> dict | None:
        """Wait synchronously for an Actor job (run or build) to finish.

        Polls the job status until it reaches a terminal state or timeout.
        Handles 404 errors gracefully (job might not exist yet in replicas).

        Args:
            url: Full URL to the job endpoint.
            params: Base query parameters to include in each request.
            wait_duration: Maximum time to wait (None = indefinite).

        Returns:
            Job data dict when finished, or None if job doesn't exist after
            DEFAULT_WAIT_WHEN_JOB_NOT_EXIST seconds.

        Raises:
            ApifyApiError: If API returns errors other than 404.
        """
        started_at = datetime.now(timezone.utc)
        should_repeat = True
        job: dict | None = None
        seconds_elapsed = 0.0
        wait_secs = to_seconds(wait_duration)

        while should_repeat:
            wait_for_finish = to_seconds(DEFAULT_WAIT_FOR_FINISH)
            if wait_secs is not None:
                wait_for_finish = int(wait_secs - seconds_elapsed)

            try:
                response = self._http_client.call(
                    url=url,
                    method='GET',
                    params={**params, 'waitForFinish': wait_for_finish},
                )
                job_response = response_to_dict(response)
                job = job_response.get('data') if isinstance(job_response, dict) else job_response
                seconds_elapsed = (datetime.now(timezone.utc) - started_at).total_seconds()

                if not isinstance(job, dict):
                    raise ApifyClientError(
                        f'Unexpected response format received from the API. '
                        f'Expected dict with "status" field, got: {type(job).__name__}'
                    )

                is_terminal = ActorJobStatus(job['status']).is_terminal
                is_timed_out = wait_secs is not None and seconds_elapsed >= wait_secs
                if is_terminal or is_timed_out:
                    should_repeat = False

                if not should_repeat:
                    # Early return here so that we avoid the sleep below if not needed
                    return job

            except ApifyApiError as exc:
                catch_not_found_or_throw(exc)

                # If there are still not found errors after DEFAULT_WAIT_WHEN_JOB_NOT_EXIST, we give up
                # and return None. In such case, the requested record probably really doesn't exist.
                if seconds_elapsed > DEFAULT_WAIT_WHEN_JOB_NOT_EXIST.total_seconds():
                    return None

            # It might take some time for database replicas to get up-to-date so sleep a bit before retrying
            time.sleep(0.25)

        return job


class ResourceClientAsync(metaclass=WithLogDetailsClient):
    """Base class for asynchronous resource clients.

    Provides URL building, parameter handling, and client creation utilities.
    All methods are synchronous and don't perform I/O operations.
    """

    def __init__(
        self,
        *,
        base_url: str,
        public_base_url: str,
        http_client: AsyncHttpClient,
        resource_path: str,
        client_registry: ClientRegistryAsync,
        resource_id: str | None = None,
        params: dict | None = None,
    ) -> None:
        """Initialize the resource client.

        Args:
            base_url: API base URL.
            public_base_url: Public CDN base URL.
            http_client: HTTP client for making requests.
            resource_path: Resource endpoint path (e.g., 'actors', 'datasets').
            client_registry: Bundle of client classes for dependency injection.
            resource_id: Optional resource ID for single-resource clients.
            params: Optional default parameters for all requests.
        """
        if resource_path.endswith('/'):
            raise ValueError('resource_path must not end with "/"')

        self._base_url = base_url
        self._public_base_url = public_base_url
        self._http_client = http_client
        self._default_params = params or {}
        self._resource_path = resource_path
        self._resource_id = resource_id
        self._client_registry = client_registry

    @property
    def resource_id(self) -> str | None:
        """Get the resource ID."""
        return self._resource_id

    @property
    def _resource_url(self) -> str:
        """Build the full resource URL from base URL, path, and optional ID."""
        url = f'{self._base_url}/{self._resource_path}'
        if self._resource_id is not None:
            url = f'{url}/{to_safe_id(self._resource_id)}'
        return url

    @cached_property
    def _base_client_kwargs(self) -> dict[str, Any]:
        """Base kwargs for creating nested/child clients.

        Returns dict with base_url, public_base_url, http_client, and client_registry. Caller adds
        resource_path, resource_id, and params as needed.
        """
        return {
            'base_url': self._resource_url,
            'public_base_url': self._public_base_url,
            'http_client': self._http_client,
            'client_registry': self._client_registry,
        }

    def _build_url(
        self,
        path: str | None = None,
        *,
        public: bool = False,
        params: dict | None = None,
    ) -> str:
        """Build complete URL for API request.

        Args:
            path: Optional path segment to append (e.g., 'runs', 'items').
            public: Whether to use public CDN URL instead of API URL.
            params: Optional query parameters to append.

        Returns:
            Complete URL with optional path and query string.
        """
        url = f'{self._resource_url}/{path}' if path else self._resource_url

        if public:
            if not url.startswith(self._base_url):
                raise ValueError(f'URL {url} does not start with base URL {self._base_url}')
            url = url.replace(self._base_url, self._public_base_url, 1)

        if params:
            filtered = {k: v for k, v in params.items() if v is not None}
            if filtered:
                separator = '&' if '?' in url else '?'
                url += separator + urlencode(filtered)

        return url

    def _build_params(self, **kwargs: Any) -> dict:
        """Merge default params with method params, filtering out None values.

        Args:
            **kwargs: Method-specific parameters to merge.

        Returns:
            Merged parameters with None values removed.
        """
        merged = {**self._default_params, **kwargs}
        return {k: v for k, v in merged.items() if v is not None}

    async def _wait_for_finish(
        self,
        url: str,
        params: dict,
        wait_duration: timedelta | None = None,
    ) -> dict | None:
        """Wait asynchronously for an Actor job (run or build) to finish.

        Polls the job status until it reaches a terminal state or timeout.
        Handles 404 errors gracefully (job might not exist yet in replicas).

        Args:
            url: Full URL to the job endpoint.
            params: Base query parameters to include in each request.
            wait_duration: Maximum time to wait (None = indefinite).

        Returns:
            Job data dict when finished, or None if job doesn't exist after
            DEFAULT_WAIT_WHEN_JOB_NOT_EXIST seconds.

        Raises:
            ApifyApiError: If API returns errors other than 404.
        """
        started_at = datetime.now(timezone.utc)
        should_repeat = True
        job: dict | None = None
        seconds_elapsed = 0.0
        wait_secs = wait_duration.total_seconds() if wait_duration is not None else None

        while should_repeat:
            wait_for_finish = int(DEFAULT_WAIT_FOR_FINISH.total_seconds())
            if wait_secs is not None:
                wait_for_finish = int(wait_secs - seconds_elapsed)

            try:
                response = await self._http_client.call(
                    url=url,
                    method='GET',
                    params={**params, 'waitForFinish': wait_for_finish},
                )
                job_response = response_to_dict(response)
                job = job_response.get('data') if isinstance(job_response, dict) else job_response

                if not isinstance(job, dict):
                    raise ApifyClientError(
                        f'Unexpected response format received from the API. '
                        f'Expected dict with "status" field, got: {type(job).__name__}'
                    )

                seconds_elapsed = (datetime.now(timezone.utc) - started_at).total_seconds()
                is_terminal = ActorJobStatus(job['status']).is_terminal
                is_timed_out = wait_secs is not None and seconds_elapsed >= wait_secs
                if is_terminal or is_timed_out:
                    should_repeat = False

                if not should_repeat:
                    # Early return here so that we avoid the sleep below if not needed
                    return job

            except ApifyApiError as exc:
                catch_not_found_or_throw(exc)

                # If there are still not found errors after DEFAULT_WAIT_WHEN_JOB_NOT_EXIST, we give up
                # and return None. In such case, the requested record probably really doesn't exist.
                if seconds_elapsed > DEFAULT_WAIT_WHEN_JOB_NOT_EXIST.total_seconds():
                    return None

            # It might take some time for database replicas to get up-to-date so sleep a bit before retrying
            await asyncio.sleep(0.25)

        return job
