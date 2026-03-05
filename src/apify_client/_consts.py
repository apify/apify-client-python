from __future__ import annotations

from datetime import timedelta

from apify_client._models import ActorJobStatus

DEFAULT_API_URL = 'https://api.apify.com'
"""Default base URL for the Apify API."""

API_VERSION = 'v2'
"""Current Apify API version."""

DEFAULT_TIMEOUT_SHORT = timedelta(seconds=5)
"""Default timeout for fast CRUD operations (e.g., get, update, delete)."""

DEFAULT_TIMEOUT_MEDIUM = timedelta(seconds=30)
"""Default timeout for batch, list, and data transfer operations."""

DEFAULT_TIMEOUT_LONG = timedelta(seconds=360)
"""Default timeout for long-polling, streaming, and other heavy operations."""

DEFAULT_TIMEOUT_MAX = timedelta(seconds=360)
"""Default maximum timeout cap for individual API requests (limits exponential growth)."""

DEFAULT_MAX_RETRIES = 4
"""Default maximum number of retries for failed requests."""

DEFAULT_MIN_DELAY_BETWEEN_RETRIES = timedelta(milliseconds=500)
"""Default minimum delay between retries."""

DEFAULT_WAIT_FOR_FINISH = timedelta(seconds=999999)
"""Default maximum wait time for job completion (effectively infinite)."""

DEFAULT_WAIT_WHEN_JOB_NOT_EXIST = timedelta(seconds=3)
"""How long to wait for a job to exist before giving up."""

TERMINAL_STATUSES = frozenset(
    {
        ActorJobStatus.SUCCEEDED,
        ActorJobStatus.FAILED,
        ActorJobStatus.TIMED_OUT,
        ActorJobStatus.ABORTED,
    }
)
"""Set of terminal Actor job statuses that indicate the job has finished."""

OVERRIDABLE_DEFAULT_HEADERS = {'Accept', 'Authorization', 'Accept-Encoding', 'User-Agent'}
"""Headers that can be overridden by users, but will trigger a warning if they do so, as it may lead to API errors."""
