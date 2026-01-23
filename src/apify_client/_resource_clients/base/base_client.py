from __future__ import annotations

import asyncio
import math
import time
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from apify_shared.consts import ActorJobStatus

from apify_client._logging import WithLogDetailsClient
from apify_client._utils import catch_not_found_or_throw, response_to_dict, to_safe_id
from apify_client.errors import ApifyApiError, ApifyClientError

if TYPE_CHECKING:
    from apify_client._client import ApifyClient, ApifyClientAsync
    from apify_client._http_client import HTTPClient, HTTPClientAsync

DEFAULT_WAIT_FOR_FINISH_SEC = 999999

# After how many seconds we give up trying in case job doesn't exist
DEFAULT_WAIT_WHEN_JOB_NOT_EXIST_SEC = 3


class BaseClient(metaclass=WithLogDetailsClient):
    """Base class for sub-clients manipulating a single resource."""

    resource_id: str | None
    url: str
    params: dict
    http_client: HTTPClient
    root_client: ApifyClient

    def __init__(
        self,
        *,
        base_url: str,
        root_client: ApifyClient,
        http_client: HTTPClient,
        resource_id: str | None = None,
        resource_path: str,
        params: dict | None = None,
    ) -> None:
        """Initialize a new instance.

        Args:
            base_url: Base URL of the API server.
            root_client: The ApifyClient instance under which this resource client exists.
            http_client: The HTTPClient instance to be used in this client.
            resource_id: ID of the manipulated resource, in case of a single-resource client.
            resource_path: Path to the resource's endpoint on the API server.
            params: Parameters to include in all requests from this client.
        """
        if resource_path.endswith('/'):
            raise ValueError('resource_path must not end with "/"')

        self.base_url = base_url
        self.root_client = root_client
        self.http_client = http_client
        self.params = params or {}
        self.resource_path = resource_path
        self.resource_id = resource_id
        self.url = f'{self.base_url}/{self.resource_path}'
        if self.resource_id is not None:
            self.safe_id = to_safe_id(self.resource_id)
            self.url = f'{self.url}/{self.safe_id}'

    def _url(self, path: str | None = None, *, public: bool = False) -> str:
        url = f'{self.url}/{path}' if path is not None else self.url

        if public:
            if not url.startswith(self.root_client.base_url):
                raise ValueError('API based URL has to start with `self.root_client.base_url`')
            return url.replace(self.root_client.base_url, self.root_client.public_base_url, 1)
        return url

    def _params(self, **kwargs: Any) -> dict:
        return {
            **self.params,
            **kwargs,
        }

    def _sub_resource_init_options(self, **kwargs: Any) -> dict:
        options = {
            'base_url': self.url,
            'http_client': self.http_client,
            'params': self.params,
            'root_client': self.root_client,
        }

        return {
            **options,
            **kwargs,
        }

    def _get(self, timeout_secs: int | None = None) -> dict | None:
        try:
            response = self.http_client.call(
                url=self.url,
                method='GET',
                params=self._params(),
                timeout_secs=timeout_secs,
            )
            return response_to_dict(response)

        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

        return None

    def _update(self, updated_fields: dict, timeout_secs: int | None = None) -> dict:
        response = self.http_client.call(
            url=self._url(),
            method='PUT',
            params=self._params(),
            json=updated_fields,
            timeout_secs=timeout_secs,
        )

        return response_to_dict(response)

    def _delete(self, timeout_secs: int | None = None) -> None:
        try:
            self.http_client.call(
                url=self._url(),
                method='DELETE',
                params=self._params(),
                timeout_secs=timeout_secs,
            )

        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

    def _wait_for_finish(self, wait_secs: int | None = None) -> dict | None:
        started_at = datetime.now(timezone.utc)
        should_repeat = True
        job: dict | None = None
        seconds_elapsed = 0

        while should_repeat:
            wait_for_finish = DEFAULT_WAIT_FOR_FINISH_SEC
            if wait_secs is not None:
                wait_for_finish = wait_secs - seconds_elapsed

            try:
                response = self.http_client.call(
                    url=self._url(),
                    method='GET',
                    params=self._params(waitForFinish=wait_for_finish),
                )
                job_response = response_to_dict(response)
                job = job_response.get('data') if isinstance(job_response, dict) else job_response
                seconds_elapsed = math.floor((datetime.now(timezone.utc) - started_at).total_seconds())

                if not isinstance(job, dict):
                    raise ApifyClientError('Unexpected response format received from the API.')

                is_terminal = ActorJobStatus(job['status']).is_terminal
                is_timed_out = wait_secs is not None and seconds_elapsed >= wait_secs
                if is_terminal or is_timed_out:
                    should_repeat = False

                if not should_repeat:
                    # Early return here so that we avoid the sleep below if not needed
                    return job

            except ApifyApiError as exc:
                catch_not_found_or_throw(exc)

                # If there are still not found errors after DEFAULT_WAIT_WHEN_JOB_NOT_EXIST_SEC, we give up
                # and return None. In such case, the requested record probably really doesn't exist.
                if seconds_elapsed > DEFAULT_WAIT_WHEN_JOB_NOT_EXIST_SEC:
                    return None

            # It might take some time for database replicas to get up-to-date so sleep a bit before retrying
            time.sleep(0.25)

        return job


class BaseClientAsync(metaclass=WithLogDetailsClient):
    """Base class for async sub-clients manipulating a single resource."""

    resource_id: str | None
    url: str
    params: dict
    http_client: HTTPClientAsync
    root_client: ApifyClientAsync

    def __init__(
        self,
        *,
        base_url: str,
        root_client: ApifyClientAsync,
        http_client: HTTPClientAsync,
        resource_id: str | None = None,
        resource_path: str,
        params: dict | None = None,
    ) -> None:
        """Initialize a new instance.

        Args:
            base_url: Base URL of the API server.
            root_client: The ApifyClientAsync instance under which this resource client exists.
            http_client: The HTTPClientAsync instance to be used in this client.
            resource_id: ID of the manipulated resource, in case of a single-resource client.
            resource_path: Path to the resource's endpoint on the API server.
            params: Parameters to include in all requests from this client.
        """
        if resource_path.endswith('/'):
            raise ValueError('resource_path must not end with "/"')

        self.base_url = base_url
        self.root_client = root_client
        self.http_client = http_client
        self.params = params or {}
        self.resource_path = resource_path
        self.resource_id = resource_id
        self.url = f'{self.base_url}/{self.resource_path}'
        if self.resource_id is not None:
            self.safe_id = to_safe_id(self.resource_id)
            self.url = f'{self.url}/{self.safe_id}'

    def _url(self, path: str | None = None, *, public: bool = False) -> str:
        url = f'{self.url}/{path}' if path is not None else self.url

        if public:
            if not url.startswith(self.root_client.base_url):
                raise ValueError('API based URL has to start with `self.root_client.base_url`')
            return url.replace(self.root_client.base_url, self.root_client.public_base_url, 1)
        return url

    def _params(self, **kwargs: Any) -> dict:
        return {
            **self.params,
            **kwargs,
        }

    def _sub_resource_init_options(self, **kwargs: Any) -> dict:
        options = {
            'base_url': self.url,
            'http_client': self.http_client,
            'params': self.params,
            'root_client': self.root_client,
        }

        return {
            **options,
            **kwargs,
        }

    async def _get(self, timeout_secs: int | None = None) -> dict | None:
        try:
            response = await self.http_client.call(
                url=self.url,
                method='GET',
                params=self._params(),
                timeout_secs=timeout_secs,
            )

            return response_to_dict(response)

        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

        return None

    async def _update(self, updated_fields: dict, timeout_secs: int | None = None) -> dict:
        response = await self.http_client.call(
            url=self._url(),
            method='PUT',
            params=self._params(),
            json=updated_fields,
            timeout_secs=timeout_secs,
        )

        return response_to_dict(response)

    async def _delete(self, timeout_secs: int | None = None) -> None:
        try:
            await self.http_client.call(
                url=self._url(),
                method='DELETE',
                params=self._params(),
                timeout_secs=timeout_secs,
            )

        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

    async def _wait_for_finish(self, wait_secs: int | None = None) -> dict | None:
        started_at = datetime.now(timezone.utc)
        should_repeat = True
        job: dict | None = None
        seconds_elapsed = 0

        while should_repeat:
            wait_for_finish = DEFAULT_WAIT_FOR_FINISH_SEC
            if wait_secs is not None:
                wait_for_finish = wait_secs - seconds_elapsed

            try:
                response = await self.http_client.call(
                    url=self._url(),
                    method='GET',
                    params=self._params(waitForFinish=wait_for_finish),
                )
                job_response = response_to_dict(response)
                job = job_response.get('data') if isinstance(job_response, dict) else job_response

                if not isinstance(job, dict):
                    raise ApifyClientError('Unexpected response format received from the API.')

                seconds_elapsed = math.floor((datetime.now(timezone.utc) - started_at).total_seconds())
                is_terminal = ActorJobStatus(job['status']).is_terminal
                is_timed_out = wait_secs is not None and seconds_elapsed >= wait_secs
                if is_terminal or is_timed_out:
                    should_repeat = False

                if not should_repeat:
                    # Early return here so that we avoid the sleep below if not needed
                    return job

            except ApifyApiError as exc:
                catch_not_found_or_throw(exc)

                # If there are still not found errors after DEFAULT_WAIT_WHEN_JOB_NOT_EXIST_SEC, we give up
                # and return None. In such case, the requested record probably really doesn't exist.
                if seconds_elapsed > DEFAULT_WAIT_WHEN_JOB_NOT_EXIST_SEC:
                    return None

            # It might take some time for database replicas to get up-to-date so sleep a bit before retrying
            await asyncio.sleep(0.25)

        return job
