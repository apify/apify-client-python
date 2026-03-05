from __future__ import annotations

import asyncio
import time
from datetime import UTC, datetime, timedelta
from functools import cached_property
from typing import TYPE_CHECKING, Any

from apify_client._consts import DEFAULT_WAIT_FOR_FINISH, DEFAULT_WAIT_WHEN_JOB_NOT_EXIST, TERMINAL_STATUSES
from apify_client._docs import docs_group
from apify_client._logging import WithLogDetailsClient
from apify_client._types import ActorJobResponse
from apify_client._utils import catch_not_found_or_throw, response_to_dict, to_safe_id, to_seconds
from apify_client.errors import ApifyApiError

if TYPE_CHECKING:
    from apify_client._client_registry import ClientRegistry, ClientRegistryAsync
    from apify_client._http_clients import HttpClient, HttpClientAsync
    from apify_client._types import Timeout


class ResourceClientBase(metaclass=WithLogDetailsClient):
    """Base class with shared implementation for sync and async resource clients.

    Provides URL building, parameter handling, and client creation utilities.
    """

    def __init__(
        self,
        *,
        base_url: str,
        public_base_url: str,
        http_client: Any,
        resource_path: str,
        client_registry: Any,
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
    ) -> str:
        """Build complete URL for API request.

        Args:
            path: Optional path segment to append (e.g., 'runs', 'items').
            public: Whether to use public CDN URL instead of API URL.

        Returns:
            Complete URL with optional path and query string.
        """
        url = f'{self._resource_url}/{path}' if path is not None else self._resource_url

        if public:
            if not url.startswith(self._base_url):
                raise ValueError(f'URL {url} does not start with base URL {self._base_url}')
            url = url.replace(self._base_url, self._public_base_url, 1)

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

    @staticmethod
    def _clean_json_payload(data: dict) -> dict:
        """Remove None values and empty nested dicts from an API request payload.

        The Apify API ignores missing fields but may reject fields explicitly set to None.
        Nested sub-models serialized by Pydantic may produce empty dicts when all their
        fields are None — these are also removed.

        Uses an iterative stack-based approach, analogous to _build_params for query params.
        """
        result: dict = {}
        stack: list[tuple[dict, dict]] = [(data, result)]

        while stack:
            source, target = stack.pop()
            for key, val in source.items():
                if val is None:
                    continue
                if isinstance(val, dict):
                    nested: dict = {}
                    target[key] = nested
                    stack.append((val, nested))
                else:
                    target[key] = val

        # Remove dicts that became empty after None filtering
        def _remove_empty(d: dict) -> None:
            for key in [k for k, v in d.items() if isinstance(v, dict)]:
                _remove_empty(d[key])
                if not d[key]:
                    del d[key]

        _remove_empty(result)
        return result


@docs_group('Resource clients')
class ResourceClient(ResourceClientBase):
    """Base class for synchronous resource clients."""

    def __init__(
        self,
        *,
        base_url: str,
        public_base_url: str,
        http_client: HttpClient,
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
        super().__init__(
            base_url=base_url,
            public_base_url=public_base_url,
            http_client=http_client,
            resource_path=resource_path,
            client_registry=client_registry,
            resource_id=resource_id,
            params=params,
        )

    def _get(self, *, timeout: Timeout) -> dict | None:
        """Perform a GET request for this resource, returning the parsed response or None if not found."""
        try:
            response = self._http_client.call(
                url=self._build_url(),
                method='GET',
                params=self._build_params(),
                timeout=timeout,
            )
            return response_to_dict(response)
        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)
            return None

    def _update(self, *, timeout: Timeout, **kwargs: Any) -> dict:
        """Perform a PUT request to update this resource with the given fields."""
        response = self._http_client.call(
            url=self._build_url(),
            method='PUT',
            params=self._build_params(),
            json=self._clean_json_payload(kwargs),
            timeout=timeout,
        )
        return response_to_dict(response)

    def _delete(self, *, timeout: Timeout) -> None:
        """Perform a DELETE request to delete this resource, ignoring 404 errors."""
        try:
            self._http_client.call(
                url=self._build_url(),
                method='DELETE',
                params=self._build_params(),
                timeout=timeout,
            )
        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

    def _list(self, *, timeout: Timeout, **kwargs: Any) -> dict:
        """Perform a GET request to list resources."""
        response = self._http_client.call(
            url=self._build_url(),
            method='GET',
            params=self._build_params(**kwargs),
            timeout=timeout,
        )
        return response_to_dict(response)

    def _create(self, *, timeout: Timeout, **kwargs: Any) -> dict:
        """Perform a POST request to create a resource."""
        response = self._http_client.call(
            url=self._build_url(),
            method='POST',
            params=self._build_params(),
            json=self._clean_json_payload(kwargs),
            timeout=timeout,
        )
        return response_to_dict(response)

    def _get_or_create(
        self,
        *,
        name: str | None = None,
        resource_fields: dict | None = None,
        timeout: Timeout,
    ) -> dict:
        """Perform a POST request to get or create a named resource."""
        response = self._http_client.call(
            url=self._build_url(),
            method='POST',
            params=self._build_params(name=name),
            json=self._clean_json_payload(resource_fields) if resource_fields is not None else None,
            timeout=timeout,
        )
        return response_to_dict(response)

    def _wait_for_finish(
        self,
        *,
        url: str,
        params: dict,
        timeout: Timeout,
        wait_duration: timedelta | None = None,
    ) -> dict | None:
        """Wait synchronously for an Actor job (run or build) to finish.

        Polls the job status until it reaches a terminal state or timeout.
        Handles 404 errors gracefully (job might not exist yet in replicas).

        Args:
            url: Full URL to the job endpoint.
            params: Base query parameters to include in each request.
            timeout: Timeout for each individual HTTP request.
            wait_duration: Maximum time to wait (None = indefinite).

        Returns:
            Job data dict when finished, or None if job doesn't exist after
            DEFAULT_WAIT_WHEN_JOB_NOT_EXIST seconds.

        Raises:
            ApifyApiError: If API returns errors other than 404.
        """
        now = datetime.now(UTC)
        deadline = (now + wait_duration) if wait_duration is not None else None
        not_found_deadline = now + DEFAULT_WAIT_WHEN_JOB_NOT_EXIST
        actor_job: dict = {}

        while True:
            if deadline is not None:
                remaining_secs = max(0, int(to_seconds(deadline - datetime.now(UTC))))
                wait_for_finish = remaining_secs
            else:
                wait_for_finish = to_seconds(DEFAULT_WAIT_FOR_FINISH, as_int=True)

            try:
                response = self._http_client.call(
                    url=url,
                    method='GET',
                    params={**params, 'waitForFinish': wait_for_finish},
                    timeout=timeout,
                )
                result = response_to_dict(response)
                actor_job_response = ActorJobResponse.model_validate(result)
                actor_job = actor_job_response.data.model_dump()

                is_terminal = actor_job_response.data.status in TERMINAL_STATUSES
                is_timed_out = deadline is not None and datetime.now(UTC) >= deadline

                if is_terminal or is_timed_out:
                    break

            except ApifyApiError as exc:
                catch_not_found_or_throw(exc)

                # If there are still not found errors after DEFAULT_WAIT_WHEN_JOB_NOT_EXIST, we give up
                # and return None. In such case, the requested record probably really doesn't exist.
                if datetime.now(UTC) > not_found_deadline:
                    return None

            # It might take some time for database replicas to get up-to-date so sleep a bit before retrying
            time.sleep(0.25)

        return actor_job


@docs_group('Resource clients')
class ResourceClientAsync(ResourceClientBase):
    """Base class for asynchronous resource clients."""

    def __init__(
        self,
        *,
        base_url: str,
        public_base_url: str,
        http_client: HttpClientAsync,
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
        super().__init__(
            base_url=base_url,
            public_base_url=public_base_url,
            http_client=http_client,
            resource_path=resource_path,
            client_registry=client_registry,
            resource_id=resource_id,
            params=params,
        )

    async def _get(self, *, timeout: Timeout) -> dict | None:
        """Perform a GET request for this resource, returning the parsed response or None if not found."""
        try:
            response = await self._http_client.call(
                url=self._build_url(),
                method='GET',
                params=self._build_params(),
                timeout=timeout,
            )
            return response_to_dict(response)
        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)
            return None

    async def _update(self, *, timeout: Timeout, **kwargs: Any) -> dict:
        """Perform a PUT request to update this resource with the given fields."""
        response = await self._http_client.call(
            url=self._build_url(),
            method='PUT',
            params=self._build_params(),
            json=self._clean_json_payload(kwargs),
            timeout=timeout,
        )
        return response_to_dict(response)

    async def _delete(self, *, timeout: Timeout) -> None:
        """Perform a DELETE request to delete this resource, ignoring 404 errors."""
        try:
            await self._http_client.call(
                url=self._build_url(),
                method='DELETE',
                params=self._build_params(),
                timeout=timeout,
            )
        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

    async def _list(self, *, timeout: Timeout, **kwargs: Any) -> dict:
        """Perform a GET request to list resources."""
        response = await self._http_client.call(
            url=self._build_url(),
            method='GET',
            params=self._build_params(**kwargs),
            timeout=timeout,
        )
        return response_to_dict(response)

    async def _create(self, *, timeout: Timeout, **kwargs: Any) -> dict:
        """Perform a POST request to create a resource."""
        response = await self._http_client.call(
            url=self._build_url(),
            method='POST',
            params=self._build_params(),
            json=self._clean_json_payload(kwargs),
            timeout=timeout,
        )
        return response_to_dict(response)

    async def _get_or_create(
        self,
        *,
        name: str | None = None,
        resource_fields: dict | None = None,
        timeout: Timeout,
    ) -> dict:
        """Perform a POST request to get or create a named resource."""
        response = await self._http_client.call(
            url=self._build_url(),
            method='POST',
            params=self._build_params(name=name),
            json=self._clean_json_payload(resource_fields) if resource_fields is not None else None,
            timeout=timeout,
        )
        return response_to_dict(response)

    async def _wait_for_finish(
        self,
        *,
        url: str,
        params: dict,
        timeout: Timeout,
        wait_duration: timedelta | None = None,
    ) -> dict | None:
        """Wait asynchronously for an Actor job (run or build) to finish.

        Polls the job status until it reaches a terminal state or timeout.
        Handles 404 errors gracefully (job might not exist yet in replicas).

        Args:
            url: Full URL to the job endpoint.
            params: Base query parameters to include in each request.
            timeout: Timeout for each individual HTTP request.
            wait_duration: Maximum time to wait (None = indefinite).

        Returns:
            Job data dict when finished, or None if job doesn't exist after
            DEFAULT_WAIT_WHEN_JOB_NOT_EXIST seconds.

        Raises:
            ApifyApiError: If API returns errors other than 404.
        """
        now = datetime.now(UTC)
        deadline = (now + wait_duration) if wait_duration is not None else None
        not_found_deadline = now + DEFAULT_WAIT_WHEN_JOB_NOT_EXIST
        actor_job: dict = {}

        while True:
            if deadline is not None:
                remaining_secs = max(0, int(to_seconds(deadline - datetime.now(UTC))))
                wait_for_finish = remaining_secs
            else:
                wait_for_finish = to_seconds(DEFAULT_WAIT_FOR_FINISH, as_int=True)

            try:
                response = await self._http_client.call(
                    url=url,
                    method='GET',
                    params={**params, 'waitForFinish': wait_for_finish},
                    timeout=timeout,
                )
                result = response_to_dict(response)
                actor_job_response = ActorJobResponse.model_validate(result)
                actor_job = actor_job_response.data.model_dump()

                is_terminal = actor_job_response.data.status in TERMINAL_STATUSES
                is_timed_out = deadline is not None and datetime.now(UTC) >= deadline

                if is_terminal or is_timed_out:
                    break

            except ApifyApiError as exc:
                catch_not_found_or_throw(exc)

                # If there are still not found errors after DEFAULT_WAIT_WHEN_JOB_NOT_EXIST, we give up
                # and return None. In such case, the requested record probably really doesn't exist.
                if datetime.now(UTC) > not_found_deadline:
                    return None

            # It might take some time for database replicas to get up-to-date so sleep a bit before retrying
            await asyncio.sleep(0.25)

        return actor_job
