from __future__ import annotations

import asyncio
import inspect
import secrets
import string
import time
from collections.abc import AsyncIterator, Iterator
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal, Protocol, TypeVar, cast, overload

import pytest

from apify_client.errors import ApifyApiError

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from apify_client import ApifyClient, ApifyClientAsync
    from apify_client._models import Actor, EnvVar, Schedule, Task, Version
    from apify_client._resource_clients import (
        ActorClient,
        ActorClientAsync,
        ActorVersionClient,
        ActorVersionClientAsync,
    )

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


async def maybe_await(value: Awaitable[T] | T) -> T:
    """Await `value` if it is awaitable, otherwise return it unchanged.

    Enables unified test code for both sync and async clients:
        result = await maybe_await(client.datasets().list())
    """
    if inspect.isawaitable(value):
        return await cast('Awaitable[T]', value)
    return value


async def maybe_sleep(seconds: float, *, is_async: bool) -> None:
    """Sleep using asyncio or time.sleep based on client type."""
    if is_async:
        await asyncio.sleep(seconds)
    else:
        time.sleep(seconds)  # noqa: ASYNC251


@overload
async def poll_until_condition(
    fn: Callable[[], Awaitable[T]],
    condition: Callable[[T], bool] = ...,
    *,
    timeout: float = ...,
    poll_interval: float = ...,
    backoff_factor: float = ...,
) -> T: ...
@overload
async def poll_until_condition(
    fn: Callable[[], T],
    condition: Callable[[T], bool] = ...,
    *,
    timeout: float = ...,
    poll_interval: float = ...,
    backoff_factor: float = ...,
) -> T: ...
async def poll_until_condition(
    fn: Callable[[], Awaitable[T] | T],
    condition: Callable[[T], bool] = bool,
    *,
    timeout: float = 30,
    poll_interval: float = 1,
    backoff_factor: float = 1,
) -> T:
    """Poll `fn` until `condition(result)` is True or the timeout expires.

    Polls `fn` at `poll_interval`-second intervals until `condition` is satisfied or `timeout` seconds have elapsed.
    Returns the last polled result regardless of whether the condition was met, so the caller can run its own
    assertion. The default condition checks for a truthy result.

    Use this instead of a fixed `asyncio.sleep` when waiting for eventually-consistent state (e.g. a freshly
    created resource appearing in a listing) that may take a variable amount of time to propagate. For highly
    variable wait times (e.g. an Actor run container starting up), pass `backoff_factor` > 1 to multiply the
    interval after each poll, covering a long timeout with few calls.
    """
    deadline = time.monotonic() + timeout
    delay = poll_interval
    result = await maybe_await(fn())
    while not condition(result):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        await asyncio.sleep(min(delay, remaining))
        delay *= backoff_factor
        result = await maybe_await(fn())
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
        is_async: Whether the iterator is async (and so are sleeps).
        max_attempts: Maximum number of polling rounds, guaranteed regardless of how long each drain takes.
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

    # Loop on attempt count rather than a wall-clock deadline: drains take HTTP time, and charging it
    # against a deadline would mean fewer retries under load — exactly when they are needed most.
    collected = await drain()
    for _ in range(max_attempts - 1):
        if expected_ids.issubset(item.id for item in collected):
            break
        await maybe_sleep(interval, is_async=is_async)
        collected = await drain()
    return collected


ConflictErrorType = Literal[
    'actor-name-not-unique',
    'actor-task-name-not-unique',
    'schedule-name-not-unique',
    'version-already-exists',
    'env-var-already-exists',
]
"""API error types signalling that a create request lost the resource's unique name or version number.

Kept a closed set rather than a plain `str` so a typo in a call below fails the type check instead of silently
disabling the recovery it was meant to enable. The values and their status codes come from the API itself - the
`*-not-unique` ones are 409, `version-already-exists` and `env-var-already-exists` are 403.
"""


async def _create_with_conflict_recovery(
    create: Callable[[], Awaitable[T] | T],
    recover: Callable[[], Awaitable[T | None] | T | None],
    *,
    error_type: ConflictErrorType,
    description: str,
) -> T:
    """Run `create`, recovering the resource if an already-committed retry made its name unavailable.

    The HTTP client retries requests on transient 5xx and network errors, so a create POST can commit server-side on
    one attempt yet still be retried; the retry then fails on the unique name or version number the first attempt
    just took. Integration tests only create resources under freshly generated random names, so such a failure can
    only be a self-conflict - `recover` fetches what the first attempt committed instead of letting the test flake.

    Only an API error whose `type` equals `error_type` is recovered. Anything else propagates, and so does a matching
    error whose resource cannot be found afterwards - a genuine create failure still fails the test.

    Args:
        create: No-arg callable performing the create request.
        recover: No-arg callable fetching the resource by the name the create request asked for.
        error_type: API error type identifying the name conflict for this resource.
        description: Human-readable resource description used in the failure note.

    Returns:
        The created resource, or the one an earlier attempt of the same request committed.
    """
    try:
        return await maybe_await(create())
    except ApifyApiError as exc:
        if exc.type != error_type:
            raise
        recovered = await maybe_await(recover())
        if recovered is None:
            exc.add_note(f'{description} hit {error_type} on create, but could not be retrieved afterwards.')
            raise
        return recovered


async def create_actor(client: ApifyClient | ApifyClientAsync, **kwargs: Any) -> Actor:
    """Create an Actor, recovering it if a retried create already took its name.

    Takes the same keyword arguments as `ActorCollectionClient.create` and requires `name` among them. See
    `_create_with_conflict_recovery` for why the recovery is needed.
    """
    name = kwargs['name']

    async def recover() -> Actor | None:
        user = await maybe_await(client.user().get())
        assert user is not None
        return await maybe_await(client.actor(f'{user.username}/{name}').get())

    return await _create_with_conflict_recovery(
        lambda: client.actors().create(**kwargs),
        recover,
        error_type='actor-name-not-unique',
        description=f'Actor {name!r}',
    )


async def create_task(client: ApifyClient | ApifyClientAsync, **kwargs: Any) -> Task:
    """Create an Actor task, recovering it if a retried create already took its name.

    Takes the same keyword arguments as `TaskCollectionClient.create` and requires `name` among them. See
    `_create_with_conflict_recovery` for why the recovery is needed.
    """
    name = kwargs['name']

    async def recover() -> Task | None:
        user = await maybe_await(client.user().get())
        assert user is not None
        return await maybe_await(client.task(f'{user.username}/{name}').get())

    return await _create_with_conflict_recovery(
        lambda: client.tasks().create(**kwargs),
        recover,
        error_type='actor-task-name-not-unique',
        description=f'task {name!r}',
    )


async def create_schedule(client: ApifyClient | ApifyClientAsync, **kwargs: Any) -> Schedule:
    """Create a schedule, recovering it if a retried create already took its name.

    Takes the same keyword arguments as `ScheduleCollectionClient.create` and requires `name` among them. See
    `_create_with_conflict_recovery` for why the recovery is needed.
    """
    name = kwargs['name']

    async def recover() -> Schedule | None:
        # Unlike Actors and tasks, schedules can only be addressed by ID, so the committed one has to be located
        # by name in the listing. Sorting by modification date puts the just-created schedule on the first page.
        page = await maybe_await(client.schedules().list(limit=1000, desc=True))
        existing = next((schedule for schedule in page.items if schedule.name == name), None)
        if existing is None:
            return None
        return await maybe_await(client.schedule(existing.id).get())

    return await _create_with_conflict_recovery(
        lambda: client.schedules().create(**kwargs),
        recover,
        error_type='schedule-name-not-unique',
        description=f'schedule {name!r}',
    )


async def create_actor_version(actor_client: ActorClient | ActorClientAsync, **kwargs: Any) -> Version:
    """Create an Actor version, recovering it if a retried create already took its version number.

    Takes the same keyword arguments as `ActorVersionCollectionClient.create` and requires `version_number` among
    them. See `_create_with_conflict_recovery` for why the recovery is needed.
    """
    version_number = kwargs['version_number']

    return await _create_with_conflict_recovery(
        lambda: actor_client.versions().create(**kwargs),
        lambda: actor_client.version(version_number).get(),
        error_type='version-already-exists',
        description=f'Actor version {version_number!r}',
    )


async def create_env_var(version_client: ActorVersionClient | ActorVersionClientAsync, **kwargs: Any) -> EnvVar:
    """Create an Actor environment variable, recovering it if a retried create already took its name.

    Takes the same keyword arguments as `ActorEnvVarCollectionClient.create` and requires `name` among them. See
    `_create_with_conflict_recovery` for why the recovery is needed.
    """
    name = kwargs['name']

    return await _create_with_conflict_recovery(
        lambda: version_client.env_vars().create(**kwargs),
        lambda: version_client.env_var(name).get(),
        error_type='env-var-already-exists',
        description=f'env var {name!r}',
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
