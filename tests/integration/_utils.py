from __future__ import annotations

import asyncio
import inspect
import logging
import secrets
import string
import time
from collections.abc import AsyncIterator, Iterator
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Protocol, TypeVar, cast, overload

import pytest

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Coroutine

logger = logging.getLogger(__name__)

# Environment variable names for test configuration
TOKEN_ENV_VAR = 'APIFY_TEST_USER_API_TOKEN'
TOKEN_ENV_VAR_2 = 'APIFY_TEST_USER_2_API_TOKEN'
API_URL_ENV_VAR = 'APIFY_INTEGRATION_TESTS_API_URL'

T = TypeVar('T')


class _HasId(Protocol):
    """Items returned by collection `iterate()` endpoints all expose `.id`."""

    @property
    def id(self) -> str: ...


_HasIdT = TypeVar('_HasIdT', bound=_HasId)


# ============================================================================
# Data classes for test fixtures
# ============================================================================


@dataclass
class StorageFixture:
    """Base storage fixture with ID and signature."""

    id: str
    signature: str


@dataclass
class DatasetFixture(StorageFixture):
    """Dataset fixture with expected content."""

    expected_content: list


@dataclass
class KvsFixture(StorageFixture):
    """Key-value store fixture with expected content and key signatures."""

    expected_content: dict[str, Any]
    keys_signature: dict[str, str]


# ============================================================================
# Helper functions
# ============================================================================


def get_crypto_random_object_id(length: int = 17) -> str:
    """Generate a cryptographically secure random object ID."""
    chars = 'abcdefghijklmnopqrstuvwxyzABCEDFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join(secrets.choice(chars) for _ in range(length))


def get_random_string(length: int = 10) -> str:
    """Generate a random alphabetic string."""
    return ''.join(secrets.choice(string.ascii_letters) for _ in range(length))


def get_random_resource_name(label: str) -> str:
    """Generate a unique resource name containing the given label.

    Ensures the generated name does not exceed the API limit of 63 characters.
    """
    name_template = 'python-client-test-{}-{}'
    template_length = len(name_template.format('', ''))
    api_name_limit = 63
    random_id_length = 8
    label_length_limit = api_name_limit - template_length - random_id_length

    label = label.replace('_', '-')
    assert len(label) <= label_length_limit, f'Max label length is {label_length_limit}, but got {len(label)}'

    return name_template.format(label, get_crypto_random_object_id(random_id_length))


@overload
async def maybe_await(value: Coroutine[Any, Any, T]) -> T: ...


@overload
async def maybe_await(value: T) -> T: ...


async def maybe_await(value: T | Coroutine[Any, Any, T]) -> T:
    """Await coroutines, pass through other values.

    Enables unified test code for both sync and async clients:
        result = await maybe_await(client.datasets().list())
    """
    if hasattr(value, '__await__'):
        return await value  # ty: ignore[invalid-await]
    return value


async def maybe_sleep(seconds: float, *, is_async: bool) -> None:
    """Sleep using asyncio or time.sleep based on client type."""
    if is_async:
        await asyncio.sleep(seconds)
    else:
        time.sleep(seconds)  # noqa: ASYNC251


async def _maybe_await(value: Awaitable[T] | T) -> T:
    """Await `value` if it is awaitable, otherwise return it unchanged.

    Lets `call_with_exp_backoff` and `poll_until_condition` accept both sync and async callables.
    """
    if inspect.isawaitable(value):
        return await cast('Awaitable[T]', value)
    return cast('T', value)


@overload
async def call_with_exp_backoff(
    fn: Callable[[], Awaitable[T]],
    condition: Callable[[T], bool] = ...,
    *,
    max_retries: int = ...,
    base_delay: float = ...,
) -> T: ...
@overload
async def call_with_exp_backoff(
    fn: Callable[[], T],
    condition: Callable[[T], bool] = ...,
    *,
    max_retries: int = ...,
    base_delay: float = ...,
) -> T: ...
async def call_with_exp_backoff(
    fn: Callable[[], Awaitable[T] | T],
    condition: Callable[[T], bool] = bool,
    *,
    max_retries: int = 5,
    base_delay: float = 1.0,
) -> T:
    """Call `fn`, retrying with exponential backoff until `condition(result)` is True.

    Calls `fn` and checks whether `condition` holds for its result. If it does not, `fn` is retried up to
    `max_retries` times, sleeping `base_delay * 2 ** attempt` seconds before each retry. The last result is
    returned regardless of whether the condition was ever satisfied, so the caller can run its own assertion.

    This is useful for eventually-consistent APIs where a freshly created resource may take a moment to become
    visible. The default condition checks for a truthy result. Pass `max_retries=0` to call `fn` exactly once.

    Unlike `poll_until_condition`, the delay between attempts grows exponentially rather than staying constant.
    """
    result = await _maybe_await(fn())
    for attempt in range(max_retries):
        if condition(result):
            return result
        delay = base_delay * 2**attempt
        logger.info(
            'Condition not met for %r, retrying in %ss (attempt %d/%d).', result, delay, attempt + 1, max_retries
        )
        await asyncio.sleep(delay)
        result = await _maybe_await(fn())
    return result


@overload
async def poll_until_condition(
    fn: Callable[[], Awaitable[T]],
    condition: Callable[[T], bool] = ...,
    *,
    timeout: float = ...,
    poll_interval: float = ...,
) -> T: ...
@overload
async def poll_until_condition(
    fn: Callable[[], T],
    condition: Callable[[T], bool] = ...,
    *,
    timeout: float = ...,
    poll_interval: float = ...,
) -> T: ...
async def poll_until_condition(
    fn: Callable[[], Awaitable[T] | T],
    condition: Callable[[T], bool] = bool,
    *,
    timeout: float = 5,
    poll_interval: float = 1,
) -> T:
    """Poll `fn` until `condition(result)` is True or the timeout expires.

    Polls `fn` at `poll_interval`-second intervals until `condition` is satisfied or `timeout` seconds have elapsed.
    Returns the last polled result regardless of whether the condition was met, so the caller can run its own
    assertion. The default condition checks for a truthy result.

    Use this instead of a fixed `asyncio.sleep` when waiting for eventually-consistent state (e.g. a freshly
    created resource appearing in a listing) that may take a variable amount of time to propagate. Unlike
    `call_with_exp_backoff`, the interval between polls stays constant.
    """
    deadline = time.monotonic() + timeout
    result = await _maybe_await(fn())
    while not condition(result):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        await asyncio.sleep(min(poll_interval, remaining))
        result = await _maybe_await(fn())
    return result


async def collect_iterate_until_present(
    iterator_factory: Callable[[], Iterator[_HasIdT] | AsyncIterator[_HasIdT]],
    expected_ids: set[str],
    *,
    item_type: type[_HasIdT],
    is_async: bool,
    max_attempts: int = 5,
    interval: float = 1.0,
) -> list[_HasIdT]:
    """Drain a collection `iterate()` until every expected ID is present.

    Handles eventual consistency on listing endpoints: under parallel load a freshly
    created resource may not appear in the listing for a short window. Each attempt
    builds a fresh iterator via `iterator_factory`, drains it, and stops early once
    `expected_ids` is a subset of the collected items' `.id` values. The most recent
    collection is returned regardless of whether the condition was met, so the caller
    can run its own assertion with a helpful failure message.

    Args:
        iterator_factory: No-arg callable returning a fresh iterator on each call.
        expected_ids: IDs that must all appear in the collected items.
        item_type: Asserted to match the runtime type of each yielded item.
        is_async: Whether the iterator is async.
        max_attempts: Maximum number of polling rounds.
        interval: Seconds to sleep between attempts.

    Returns:
        The most recently collected items.
    """

    async def drain() -> list[_HasIdT]:
        iterator = iterator_factory()
        collected: list[_HasIdT] = []
        if is_async:
            assert isinstance(iterator, AsyncIterator)
            async for item in iterator:
                assert isinstance(item, item_type)
                collected.append(item)
        else:
            assert isinstance(iterator, Iterator)
            for item in iterator:
                assert isinstance(item, item_type)
                collected.append(item)
        return collected

    return await poll_until_condition(
        drain,
        lambda collected: expected_ids.issubset(item.id for item in collected),
        timeout=max_attempts * interval,
        poll_interval=interval,
    )


# ============================================================================
# Pytest markers and parametrization
# ============================================================================

parametrized_api_urls = pytest.mark.parametrize(
    ('api_url', 'api_public_url'),
    [
        ('https://api.apify.com', 'https://api.apify.com'),
        ('https://api.apify.com', None),
        ('https://api.apify.com', 'https://custom-public-url.com'),
        ('https://api.apify.com', 'https://custom-public-url.com/with/custom/path'),
        ('https://api.apify.com', 'https://custom-public-url.com/with/custom/path/'),
        ('http://10.0.88.214:8010', 'https://api.apify.com'),
        ('http://10.0.88.214:8010', None),
    ],
)
"""Parametrize decorator for testing various API URL and public URL combinations."""
