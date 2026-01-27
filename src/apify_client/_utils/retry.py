"""Utilities for retrying operations with exponential backoff."""

from __future__ import annotations

import asyncio
import random
import time
from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

T = TypeVar('T')


def retry_with_exp_backoff(
    func: Callable[[Callable[[], None], int], T],
    *,
    max_retries: int = 8,
    backoff_base_millis: int = 500,
    backoff_factor: float = 2,
    random_factor: float = 1,
) -> T:
    """Retry a function with exponential backoff.

    Args:
        func: Function to retry. Receives a stop_retrying callback and attempt number.
        max_retries: Maximum number of retry attempts.
        backoff_base_millis: Base backoff delay in milliseconds.
        backoff_factor: Exponential backoff multiplier (1-10).
        random_factor: Random jitter factor (0-1).

    Returns:
        The return value of the function.
    """
    random_factor = min(max(0, random_factor), 1)
    backoff_factor = min(max(1, backoff_factor), 10)
    swallow = True

    def stop_retrying() -> None:
        nonlocal swallow
        swallow = False

    for attempt in range(1, max_retries + 1):
        try:
            return func(stop_retrying, attempt)
        except Exception:
            if not swallow:
                raise

        random_sleep_factor = random.uniform(1, 1 + random_factor)
        backoff_base_secs = backoff_base_millis / 1000
        backoff_exp_factor = backoff_factor ** (attempt - 1)

        sleep_time_secs = random_sleep_factor * backoff_base_secs * backoff_exp_factor
        time.sleep(sleep_time_secs)

    return func(stop_retrying, max_retries + 1)


async def retry_with_exp_backoff_async(
    async_func: Callable[[Callable[[], None], int], Awaitable[T]],
    *,
    max_retries: int = 8,
    backoff_base_millis: int = 500,
    backoff_factor: float = 2,
    random_factor: float = 1,
) -> T:
    """Retry an async function with exponential backoff.

    Args:
        async_func: Async function to retry. Receives a stop_retrying callback and attempt number.
        max_retries: Maximum number of retry attempts.
        backoff_base_millis: Base backoff delay in milliseconds.
        backoff_factor: Exponential backoff multiplier (1-10).
        random_factor: Random jitter factor (0-1).

    Returns:
        The return value of the async function.
    """
    random_factor = min(max(0, random_factor), 1)
    backoff_factor = min(max(1, backoff_factor), 10)
    swallow = True

    def stop_retrying() -> None:
        nonlocal swallow
        swallow = False

    for attempt in range(1, max_retries + 1):
        try:
            return await async_func(stop_retrying, attempt)
        except Exception:
            if not swallow:
                raise

        random_sleep_factor = random.uniform(1, 1 + random_factor)
        backoff_base_secs = backoff_base_millis / 1000
        backoff_exp_factor = backoff_factor ** (attempt - 1)

        sleep_time_secs = random_sleep_factor * backoff_base_secs * backoff_exp_factor
        await asyncio.sleep(sleep_time_secs)

    return await async_func(stop_retrying, max_retries + 1)
