from __future__ import annotations

import asyncio
import time
from datetime import timedelta
from typing import TYPE_CHECKING, TypeVar

from apify_client._logging import logger
from apify_client.errors import ApifyApiError

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

T = TypeVar('T')

RESOURCE_LIMIT_ERROR_TYPES = frozenset({'actor-memory-limit-exceeded', 'concurrent-runs-limit-exceeded'})
"""Error types the API rejects a run start with while the account has no free memory or concurrent-run slot for it.

Both clear as other runs or builds finish.
"""

WAIT_FOR_RESOURCES_COOLDOWN = timedelta(seconds=10)
"""Cooldown between two attempts to start a run that was rejected for lack of resources."""


def _next_delay(exc: ApifyApiError, deadline: float | None) -> float:
    """Return the seconds to sleep before the next attempt, or re-raise `exc` if no attempt should follow."""
    if exc.type not in RESOURCE_LIMIT_ERROR_TYPES:
        raise exc
    delay = WAIT_FOR_RESOURCES_COOLDOWN.total_seconds()
    if deadline is not None:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise exc
        delay = min(delay, remaining)
    logger.info('Not enough resources to start the run (%s), retrying in %gs.', exc.type, delay)
    return delay


def start_waiting_for_resources(start: Callable[[], T], *, wait_for_resources: bool | timedelta) -> T:
    """Make the `start` request, retrying it every `WAIT_FOR_RESOURCES_COOLDOWN` while it fails for lack of resources.

    `True` retries until the request succeeds, a `timedelta` bounds the retrying, after which the last error is raised.
    Any other error is raised right away.
    """
    if wait_for_resources is False:
        return start()
    deadline = None if wait_for_resources is True else time.monotonic() + wait_for_resources.total_seconds()
    while True:
        try:
            return start()
        except ApifyApiError as exc:
            time.sleep(_next_delay(exc, deadline))


async def start_waiting_for_resources_async(
    start: Callable[[], Awaitable[T]],
    *,
    wait_for_resources: bool | timedelta,
) -> T:
    """Async variant of `start_waiting_for_resources`."""
    if wait_for_resources is False:
        return await start()
    deadline = None if wait_for_resources is True else time.monotonic() + wait_for_resources.total_seconds()
    while True:
        try:
            return await start()
        except ApifyApiError as exc:
            await asyncio.sleep(_next_delay(exc, deadline))
