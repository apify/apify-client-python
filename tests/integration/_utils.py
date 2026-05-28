from __future__ import annotations

import asyncio
import secrets
import string
import time
from collections.abc import AsyncIterator, Iterator
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Protocol, TypeVar, overload

import pytest

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine

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
    builds a fresh iterator via `iterator_factory`, drains it, and breaks early once
    `expected_ids` is a subset of the collected items' `.id` values. The most recent
    collection is returned regardless of whether the condition was met, so the caller
    can run its own assertion with a helpful failure message.

    Args:
        iterator_factory: No-arg callable returning a fresh iterator on each call.
        expected_ids: IDs that must all appear in the collected items.
        item_type: Asserted to match the runtime type of each yielded item.
        is_async: Whether the iterator is async (and so are sleeps).
        max_attempts: Maximum number of polling rounds.
        interval: Seconds to sleep before each attempt.

    Returns:
        The most recently collected items.
    """
    collected: list[_HasIdT] = []
    for attempt in range(max_attempts):
        if attempt > 0:
            await maybe_sleep(interval, is_async=is_async)
        iterator = iterator_factory()
        collected = []
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
        if expected_ids.issubset(item.id for item in collected):
            break
    return collected


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
