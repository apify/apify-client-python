"""Utilities for waiting on Actor jobs to finish."""

from __future__ import annotations

import asyncio
import math
import time
from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apify_client._http_client import HttpClient, HttpClientAsync

from apify_client._consts import (
    DEFAULT_WAIT_FOR_FINISH_SEC,
    DEFAULT_WAIT_WHEN_JOB_NOT_EXIST_SEC,
    ActorJobStatus,
)
from apify_client._utils.errors import catch_not_found_or_throw
from apify_client._utils.response import response_to_dict
from apify_client.errors import ApifyApiError, ApifyClientError


def wait_for_finish_sync(
    http_client: HttpClient,
    url: str,
    params: dict,
    wait_secs: int | None = None,
) -> dict | None:
    """Wait synchronously for an Actor job (run or build) to finish.

    Polls the job status until it reaches a terminal state or timeout.
    Handles 404 errors gracefully (job might not exist yet in replicas).

    Args:
        http_client: HTTP client instance for making requests
        url: Full URL to the job endpoint
        params: Base query parameters to include in each request
        wait_secs: Maximum seconds to wait (None = indefinite)

    Returns:
        Job data dict when finished, or None if job doesn't exist after
        DEFAULT_WAIT_WHEN_JOB_NOT_EXIST_SEC seconds

    Raises:
        ApifyApiError: If API returns errors other than 404
    """
    started_at = datetime.now(timezone.utc)
    should_repeat = True
    job: dict | None = None
    seconds_elapsed = 0

    while should_repeat:
        wait_for_finish = DEFAULT_WAIT_FOR_FINISH_SEC
        if wait_secs is not None:
            wait_for_finish = wait_secs - seconds_elapsed

        try:
            response = http_client.call(
                url=url,
                method='GET',
                params={**params, 'waitForFinish': wait_for_finish},
            )
            job_response = response_to_dict(response)
            job = job_response.get('data') if isinstance(job_response, dict) else job_response
            seconds_elapsed = math.floor((datetime.now(timezone.utc) - started_at).total_seconds())

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

            # If there are still not found errors after DEFAULT_WAIT_WHEN_JOB_NOT_EXIST_SEC, we give up
            # and return None. In such case, the requested record probably really doesn't exist.
            if seconds_elapsed > DEFAULT_WAIT_WHEN_JOB_NOT_EXIST_SEC:
                return None

        # It might take some time for database replicas to get up-to-date so sleep a bit before retrying
        time.sleep(0.25)

    return job


async def wait_for_finish_async(
    http_client: HttpClientAsync,
    url: str,
    params: dict,
    wait_secs: int | None = None,
) -> dict | None:
    """Wait asynchronously for an Actor job (run or build) to finish.

    Polls the job status until it reaches a terminal state or timeout.
    Handles 404 errors gracefully (job might not exist yet in replicas).

    Args:
        http_client: Async HTTP client instance for making requests
        url: Full URL to the job endpoint
        params: Base query parameters to include in each request
        wait_secs: Maximum seconds to wait (None = indefinite)

    Returns:
        Job data dict when finished, or None if job doesn't exist after
        DEFAULT_WAIT_WHEN_JOB_NOT_EXIST_SEC seconds

    Raises:
        ApifyApiError: If API returns errors other than 404
    """
    started_at = datetime.now(timezone.utc)
    should_repeat = True
    job: dict | None = None
    seconds_elapsed = 0

    while should_repeat:
        wait_for_finish = DEFAULT_WAIT_FOR_FINISH_SEC
        if wait_secs is not None:
            wait_for_finish = wait_secs - seconds_elapsed

        try:
            response = await http_client.call(
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
