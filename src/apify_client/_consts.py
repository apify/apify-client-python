from __future__ import annotations

from datetime import timedelta
from typing import Any

from apify_client._models import ActorJobStatus

JsonSerializable = str | int | float | bool | None | dict[str, Any] | list[Any]
"""Type for representing json-serializable values. It's close enough to the real thing supported by json.parse.
It was suggested in a discussion with (and approved by) Guido van Rossum, so I'd consider it correct enough.
"""

DEFAULT_API_URL = 'https://api.apify.com'
"""Default base URL for the Apify API."""

API_VERSION = 'v2'
"""Current Apify API version."""

DEFAULT_TIMEOUT = timedelta(seconds=360)
"""Default request timeout."""

DEFAULT_MAX_RETRIES = 8
"""Default maximum number of retries for failed requests."""

DEFAULT_MIN_DELAY_BETWEEN_RETRIES = timedelta(milliseconds=500)
"""Default minimum delay between retries."""


DEFAULT_WAIT_FOR_FINISH = timedelta(seconds=999999)
"""Default maximum wait time for job completion (effectively infinite)."""

DEFAULT_WAIT_WHEN_JOB_NOT_EXIST = timedelta(seconds=3)
"""How long to wait for a job to exist before giving up."""

FAST_OPERATION_TIMEOUT = timedelta(seconds=5)
"""Timeout for fast, idempotent operations (e.g., GET, DELETE)."""

STANDARD_OPERATION_TIMEOUT = timedelta(seconds=30)
"""Timeout for operations that may take longer (e.g., list operations, batch operations)."""

TERMINAL_STATUSES = frozenset(
    {
        ActorJobStatus.SUCCEEDED,
        ActorJobStatus.FAILED,
        ActorJobStatus.TIMED_OUT,
        ActorJobStatus.ABORTED,
    }
)
"""Set of terminal Actor job statuses that indicate the job has finished."""
