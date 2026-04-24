"""Return types for paginated list methods.

Aligned with the JS client's `Promise<Result> & AsyncIterable<Item>` pattern
(apify/apify-client-js#803).

**Design:**

- `IterableListPage[T]` is a minimal base: it holds the page-crossing iterator produced by the
  builder and exposes it via `__iter__`. No fields, no fallback logic.
- Per-endpoint subclasses (e.g. `IterableListOfWebhooks`) manually declare **exactly** the fields
  their API response carries. No Pydantic ancestry, so no LSP violation on `__iter__`, and no
  fake fields that don't exist for a given endpoint (e.g. `ListOfKeys` has `is_truncated` and no
  `offset`; `ListOfRequests` has `cursor`/`next_cursor` and no `total`).
- The pagination generator lives in `build_iterable_offset` / `build_iterable_cursor`; it is
  passed into the subclass's constructor as `iterator=...`. There is no second iteration path.
- Async returns `AwaitableAsyncIterable[M, T]` — `await` resolves to the raw Pydantic `ListOf*`
  (all its fields typed); `async for` iterates items across pages.
"""

from __future__ import annotations

from collections.abc import AsyncIterable, AsyncIterator, Awaitable, Callable, Generator, Iterable, Iterator
from typing import TYPE_CHECKING, Any, Generic, Protocol, TypeVar

from apify_client._docs import docs_group


class _HasItems(Protocol):
    """Minimal page-shape used by the builders: something with `.items: list[Any]`."""

    items: list[Any]


if TYPE_CHECKING:
    from apify_client._models import (
        ActorShort,
        BuildShort,
        DatasetListItem,
        EnvVar,
        KeyValueStore,
        KeyValueStoreKey,
        ListOfActors,
        ListOfBuilds,
        ListOfDatasets,
        ListOfEnvVars,
        ListOfKeys,
        ListOfKeyValueStores,
        ListOfRequestQueues,
        ListOfRequests,
        ListOfRuns,
        ListOfSchedules,
        ListOfStoreActors,
        ListOfTasks,
        ListOfVersions,
        ListOfWebhookDispatches,
        ListOfWebhooks,
        Request,
        RequestQueueShort,
        RunShort,
        ScheduleShort,
        StoreListActor,
        TaskShort,
        Version,
        WebhookDispatch,
        WebhookShort,
    )

T = TypeVar('T')
M = TypeVar('M', bound=_HasItems)


def _min_for_limit_param(a: int | None, b: int | None) -> int | None:
    """Return minimum of two limit parameters, treating `None` or `0` as infinity.

    The Apify API treats `0` as no limit for the `limit` parameter, so `0` here means infinity.
    Returns `None` when both inputs represent infinity.
    """
    if a == 0:
        a = None
    if b == 0:
        b = None
    if a is None:
        return b
    if b is None:
        return a
    return min(a, b)


# ---------------------------------------------------------------------------
# Sync base + per-endpoint subclasses.
# ---------------------------------------------------------------------------


@docs_group('Other')
class IterableListPage(Iterable[T], Generic[T]):
    """A page of results that can also be iterated to yield items across subsequent pages.

    Iterating with `for item in ...` yields individual items and performs additional API calls
    as needed to fetch further pages. Subclasses add the endpoint-specific fields verbatim.
    """

    def __init__(self, iterator: Iterator[T]) -> None:
        """Store the page-crossing iterator produced by the builder."""
        self._iterator = iterator

    def __iter__(self) -> Iterator[T]:
        """Return the page-crossing iterator over individual items."""
        return self._iterator


@docs_group('Other')
class IterableListOfActors(IterableListPage['ActorShort']):
    """A page of Actors that iterates `ActorShort` items across API pages."""

    def __init__(
        self,
        *,
        total: int,
        offset: int,
        limit: int,
        desc: bool,
        count: int,
        items: list[ActorShort],
        iterator: Iterator[ActorShort],
    ) -> None:
        self.total = total
        self.offset = offset
        self.limit = limit
        self.desc = desc
        self.count = count
        self.items = items
        self._iterator = iterator


@docs_group('Other')
class IterableListOfBuilds(IterableListPage['BuildShort']):
    """A page of builds that iterates `BuildShort` items across API pages."""

    def __init__(
        self,
        *,
        total: int,
        offset: int,
        limit: int,
        desc: bool,
        count: int,
        items: list[BuildShort],
        iterator: Iterator[BuildShort],
    ) -> None:
        self.total = total
        self.offset = offset
        self.limit = limit
        self.desc = desc
        self.count = count
        self.items = items
        self._iterator = iterator


@docs_group('Other')
class IterableListOfDatasets(IterableListPage['DatasetListItem']):
    """A page of datasets that iterates `DatasetListItem` items across API pages."""

    def __init__(
        self,
        *,
        total: int,
        offset: int,
        limit: int,
        desc: bool,
        count: int,
        items: list[DatasetListItem],
        iterator: Iterator[DatasetListItem],
    ) -> None:
        self.total = total
        self.offset = offset
        self.limit = limit
        self.desc = desc
        self.count = count
        self.items = items
        self._iterator = iterator


@docs_group('Other')
class IterableListOfEnvVars(IterableListPage['EnvVar']):
    """A page of environment variables that iterates `EnvVar` items across API pages."""

    def __init__(
        self,
        *,
        total: int,
        items: list[EnvVar],
        iterator: Iterator[EnvVar],
    ) -> None:
        self.total = total
        self.items = items
        self._iterator = iterator


@docs_group('Other')
class IterableListOfKeyValueStores(IterableListPage['KeyValueStore']):
    """A page of key-value stores that iterates `KeyValueStore` items across API pages."""

    def __init__(
        self,
        *,
        total: int,
        offset: int,
        limit: int,
        desc: bool,
        count: int,
        items: list[KeyValueStore],
        iterator: Iterator[KeyValueStore],
    ) -> None:
        self.total = total
        self.offset = offset
        self.limit = limit
        self.desc = desc
        self.count = count
        self.items = items
        self._iterator = iterator


@docs_group('Other')
class IterableListOfKeys(IterableListPage['KeyValueStoreKey']):
    """A page of key-value store keys that iterates `KeyValueStoreKey` items across API pages.

    Uses cursor-based pagination via `exclusive_start_key` / `next_exclusive_start_key`.
    """

    def __init__(
        self,
        *,
        items: list[KeyValueStoreKey],
        count: int,
        limit: int,
        exclusive_start_key: str | None,
        is_truncated: bool,
        next_exclusive_start_key: str | None,
        iterator: Iterator[KeyValueStoreKey],
    ) -> None:
        self.items = items
        self.count = count
        self.limit = limit
        self.exclusive_start_key = exclusive_start_key
        self.is_truncated = is_truncated
        self.next_exclusive_start_key = next_exclusive_start_key
        self._iterator = iterator


@docs_group('Other')
class IterableListOfRequestQueues(IterableListPage['RequestQueueShort']):
    """A page of request queues that iterates `RequestQueueShort` items across API pages."""

    def __init__(
        self,
        *,
        total: int,
        offset: int,
        limit: int,
        desc: bool,
        count: int,
        items: list[RequestQueueShort],
        iterator: Iterator[RequestQueueShort],
    ) -> None:
        self.total = total
        self.offset = offset
        self.limit = limit
        self.desc = desc
        self.count = count
        self.items = items
        self._iterator = iterator


@docs_group('Other')
class IterableListOfRequests(IterableListPage['Request']):
    """A page of requests that iterates `Request` items across API pages.

    Uses cursor-based pagination via the opaque `cursor` / `next_cursor` tokens.
    """

    def __init__(
        self,
        *,
        items: list[Request],
        limit: int,
        count: int | None = None,
        cursor: str | None = None,
        next_cursor: str | None = None,
        exclusive_start_id: str | None = None,
        iterator: Iterator[Request],
    ) -> None:
        self.items = items
        self.limit = limit
        self.count = count
        self.cursor = cursor
        self.next_cursor = next_cursor
        self.exclusive_start_id = exclusive_start_id
        self._iterator = iterator


@docs_group('Other')
class IterableListOfRuns(IterableListPage['RunShort']):
    """A page of runs that iterates `RunShort` items across API pages."""

    def __init__(
        self,
        *,
        total: int,
        offset: int,
        limit: int,
        desc: bool,
        count: int,
        items: list[RunShort],
        iterator: Iterator[RunShort],
    ) -> None:
        self.total = total
        self.offset = offset
        self.limit = limit
        self.desc = desc
        self.count = count
        self.items = items
        self._iterator = iterator


@docs_group('Other')
class IterableListOfSchedules(IterableListPage['ScheduleShort']):
    """A page of schedules that iterates `ScheduleShort` items across API pages."""

    def __init__(
        self,
        *,
        total: int,
        offset: int,
        limit: int,
        desc: bool,
        count: int,
        items: list[ScheduleShort],
        iterator: Iterator[ScheduleShort],
    ) -> None:
        self.total = total
        self.offset = offset
        self.limit = limit
        self.desc = desc
        self.count = count
        self.items = items
        self._iterator = iterator


@docs_group('Other')
class IterableListOfStoreActors(IterableListPage['StoreListActor']):
    """A page of store Actors that iterates `StoreListActor` items across API pages."""

    def __init__(
        self,
        *,
        total: int,
        offset: int,
        limit: int,
        desc: bool,
        count: int,
        items: list[StoreListActor],
        iterator: Iterator[StoreListActor],
    ) -> None:
        self.total = total
        self.offset = offset
        self.limit = limit
        self.desc = desc
        self.count = count
        self.items = items
        self._iterator = iterator


@docs_group('Other')
class IterableListOfTasks(IterableListPage['TaskShort']):
    """A page of tasks that iterates `TaskShort` items across API pages."""

    def __init__(
        self,
        *,
        total: int,
        offset: int,
        limit: int,
        desc: bool,
        count: int,
        items: list[TaskShort],
        iterator: Iterator[TaskShort],
    ) -> None:
        self.total = total
        self.offset = offset
        self.limit = limit
        self.desc = desc
        self.count = count
        self.items = items
        self._iterator = iterator


@docs_group('Other')
class IterableListOfVersions(IterableListPage['Version']):
    """A page of Actor versions that iterates `Version` items across API pages."""

    def __init__(
        self,
        *,
        total: int,
        items: list[Version],
        iterator: Iterator[Version],
    ) -> None:
        self.total = total
        self.items = items
        self._iterator = iterator


@docs_group('Other')
class IterableListOfWebhookDispatches(IterableListPage['WebhookDispatch']):
    """A page of webhook dispatches that iterates `WebhookDispatch` items across API pages."""

    def __init__(
        self,
        *,
        total: int,
        offset: int,
        limit: int,
        desc: bool,
        count: int,
        items: list[WebhookDispatch],
        iterator: Iterator[WebhookDispatch],
    ) -> None:
        self.total = total
        self.offset = offset
        self.limit = limit
        self.desc = desc
        self.count = count
        self.items = items
        self._iterator = iterator


@docs_group('Other')
class IterableListOfWebhooks(IterableListPage['WebhookShort']):
    """A page of webhooks that iterates `WebhookShort` items across API pages."""

    def __init__(
        self,
        *,
        total: int,
        offset: int,
        limit: int,
        desc: bool,
        count: int,
        items: list[WebhookShort],
        iterator: Iterator[WebhookShort],
    ) -> None:
        self.total = total
        self.offset = offset
        self.limit = limit
        self.desc = desc
        self.count = count
        self.items = items
        self._iterator = iterator


@docs_group('Other')
class IterableDatasetItemsPage(IterableListPage[dict]):
    """A page of dataset items that iterates raw dict items across API pages.

    Dataset items are arbitrary JSON objects, so they cannot be represented by a specific
    Pydantic model — hence items are typed as `dict`.
    """

    def __init__(
        self,
        *,
        total: int,
        offset: int,
        limit: int,
        desc: bool,
        count: int,
        items: list[dict],
        iterator: Iterator[dict],
    ) -> None:
        self.total = total
        self.offset = offset
        self.limit = limit
        self.desc = desc
        self.count = count
        self.items = items
        self._iterator = iterator


# ---------------------------------------------------------------------------
# Async: generic Awaitable[M] + AsyncIterable[T].
# ---------------------------------------------------------------------------


@docs_group('Other')
class AwaitableAsyncIterable(AsyncIterable[T], Generic[M, T]):
    """A value that is both `Awaitable[M]` and `AsyncIterable[T]`.

    Mirrors JS `Promise<Result> & AsyncIterable<Item>`: callers can `await` to get `M` (the
    first page as the typed Pydantic `ListOf*`), or `async for item in ...` to iterate items
    across pages.

    A single instance supports either `await` or `async for` — not both.
    """

    def __init__(
        self,
        awaitable_factory: Callable[[], Awaitable[M]],
        async_iterator: AsyncIterator[T],
    ) -> None:
        self._awaitable_factory = awaitable_factory
        self._async_iterator = async_iterator

    def __aiter__(self) -> AsyncIterator[T]:
        return self._async_iterator

    def __await__(self) -> Generator[Any, Any, M]:
        return self._awaitable_factory().__await__()


# ---------------------------------------------------------------------------
# Builders. `fetch_page` returns the raw typed page (pydantic `ListOf*` or dict-backed
# `DatasetItemsPage`). `factory` takes the first page + iterator and constructs the
# endpoint-specific `IterableListOf*`.
# ---------------------------------------------------------------------------


R = TypeVar('R')  # return type of the sync builder — the concrete IterableListOf* subclass


# ---------------------------------------------------------------------------
# Factories mapping a Pydantic `ListOf*` page + iterator into the matching
# `IterableListOf*` subclass. Kept here so the list methods stay one-liners.
# ---------------------------------------------------------------------------


def make_iterable_list_of_actors(page: ListOfActors, it: Iterator[ActorShort]) -> IterableListOfActors:
    return IterableListOfActors(
        total=page.total,
        offset=page.offset,
        limit=page.limit,
        desc=page.desc,
        count=page.count,
        items=page.items,
        iterator=it,
    )


def make_iterable_list_of_builds(page: ListOfBuilds, it: Iterator[BuildShort]) -> IterableListOfBuilds:
    return IterableListOfBuilds(
        total=page.total,
        offset=page.offset,
        limit=page.limit,
        desc=page.desc,
        count=page.count,
        items=page.items,
        iterator=it,
    )


def make_iterable_list_of_datasets(page: ListOfDatasets, it: Iterator[DatasetListItem]) -> IterableListOfDatasets:
    return IterableListOfDatasets(
        total=page.total,
        offset=page.offset,
        limit=page.limit,
        desc=page.desc,
        count=page.count,
        items=page.items,
        iterator=it,
    )


def make_iterable_list_of_env_vars(page: ListOfEnvVars, it: Iterator[EnvVar]) -> IterableListOfEnvVars:
    return IterableListOfEnvVars(total=page.total, items=page.items, iterator=it)


def make_iterable_list_of_key_value_stores(
    page: ListOfKeyValueStores, it: Iterator[KeyValueStore]
) -> IterableListOfKeyValueStores:
    return IterableListOfKeyValueStores(
        total=page.total,
        offset=page.offset,
        limit=page.limit,
        desc=page.desc,
        count=page.count,
        items=page.items,
        iterator=it,
    )


def make_iterable_list_of_keys(page: ListOfKeys, it: Iterator[KeyValueStoreKey]) -> IterableListOfKeys:
    return IterableListOfKeys(
        items=page.items,
        count=page.count,
        limit=page.limit,
        exclusive_start_key=page.exclusive_start_key,
        is_truncated=page.is_truncated,
        next_exclusive_start_key=page.next_exclusive_start_key,
        iterator=it,
    )


def make_iterable_list_of_request_queues(
    page: ListOfRequestQueues, it: Iterator[RequestQueueShort]
) -> IterableListOfRequestQueues:
    return IterableListOfRequestQueues(
        total=page.total,
        offset=page.offset,
        limit=page.limit,
        desc=page.desc,
        count=page.count,
        items=page.items,
        iterator=it,
    )


def make_iterable_list_of_requests(page: ListOfRequests, it: Iterator[Request]) -> IterableListOfRequests:
    return IterableListOfRequests(
        items=page.items,
        limit=page.limit,
        count=page.count,
        cursor=page.cursor,
        next_cursor=page.next_cursor,
        exclusive_start_id=page.exclusive_start_id,
        iterator=it,
    )


def make_iterable_list_of_runs(page: ListOfRuns, it: Iterator[RunShort]) -> IterableListOfRuns:
    return IterableListOfRuns(
        total=page.total,
        offset=page.offset,
        limit=page.limit,
        desc=page.desc,
        count=page.count,
        items=page.items,
        iterator=it,
    )


def make_iterable_list_of_schedules(page: ListOfSchedules, it: Iterator[ScheduleShort]) -> IterableListOfSchedules:
    return IterableListOfSchedules(
        total=page.total,
        offset=page.offset,
        limit=page.limit,
        desc=page.desc,
        count=page.count,
        items=page.items,
        iterator=it,
    )


def make_iterable_list_of_store_actors(
    page: ListOfStoreActors, it: Iterator[StoreListActor]
) -> IterableListOfStoreActors:
    return IterableListOfStoreActors(
        total=page.total,
        offset=page.offset,
        limit=page.limit,
        desc=page.desc,
        count=page.count,
        items=page.items,
        iterator=it,
    )


def make_iterable_list_of_tasks(page: ListOfTasks, it: Iterator[TaskShort]) -> IterableListOfTasks:
    return IterableListOfTasks(
        total=page.total,
        offset=page.offset,
        limit=page.limit,
        desc=page.desc,
        count=page.count,
        items=page.items,
        iterator=it,
    )


def make_iterable_list_of_versions(page: ListOfVersions, it: Iterator[Version]) -> IterableListOfVersions:
    return IterableListOfVersions(total=page.total, items=page.items, iterator=it)


def make_iterable_list_of_webhook_dispatches(
    page: ListOfWebhookDispatches, it: Iterator[WebhookDispatch]
) -> IterableListOfWebhookDispatches:
    return IterableListOfWebhookDispatches(
        total=page.total,
        offset=page.offset,
        limit=page.limit,
        desc=page.desc,
        count=page.count,
        items=page.items,
        iterator=it,
    )


def make_iterable_list_of_webhooks(page: ListOfWebhooks, it: Iterator[WebhookShort]) -> IterableListOfWebhooks:
    return IterableListOfWebhooks(
        total=page.total,
        offset=page.offset,
        limit=page.limit,
        desc=page.desc,
        count=page.count,
        items=page.items,
        iterator=it,
    )


def make_iterable_dataset_items_page(page: Any, it: Iterator[dict]) -> IterableDatasetItemsPage:
    """Wrap a `DatasetItemsPage` (plain dataclass with items+headers metadata) + iterator."""
    return IterableDatasetItemsPage(
        total=page.total,
        offset=page.offset,
        limit=page.limit,
        desc=page.desc,
        count=page.count,
        items=page.items,
        iterator=it,
    )


def build_iterable_offset(
    fetch_page: Callable[..., M],
    factory: Callable[[M, Iterator[Any]], R],
    **kwargs: Any,
) -> R:
    """Build an offset-paginated sync iterable result.

    `fetch_page` is called with `{offset, limit, **kwargs}` for each page; `factory` wraps the
    first page together with the page-crossing iterator into the final `IterableListOf*`.
    """
    chunk_size = kwargs.pop('chunk_size', 0) or 0
    offset = kwargs.get('offset') or 0
    limit = kwargs.get('limit') or 0

    first_page = fetch_page(**{**kwargs, 'limit': _min_for_limit_param(kwargs.get('limit'), chunk_size)})

    def iterator() -> Iterator[Any]:
        current = first_page
        yield from current.items  # type: ignore[attr-defined]

        fetched = len(current.items)  # type: ignore[attr-defined]
        while current.items and (not limit or (limit > fetched)):  # type: ignore[attr-defined]
            new_kwargs = {
                **kwargs,
                'offset': offset + fetched,
                'limit': chunk_size if not limit else _min_for_limit_param(limit - fetched, chunk_size),
            }
            current = fetch_page(**new_kwargs)
            yield from current.items  # type: ignore[attr-defined]
            fetched += len(current.items)  # type: ignore[attr-defined]

    return factory(first_page, iterator())


def build_iterable_cursor(
    fetch_page: Callable[..., M],
    factory: Callable[[M, Iterator[Any]], R],
    *,
    cursor_param: str,
    next_cursor_fn: Callable[[Any], Any],
    initial_cursor: Any = None,
    limit: int | None = None,
    chunk_size: int | None = None,
    **kwargs: Any,
) -> R:
    """Build a cursor-paginated sync iterable result.

    Analogous to `build_iterable_offset`, but pagination uses a cursor: the callback is invoked
    with `{cursor_param: cursor, limit, **kwargs}`. `next_cursor_fn(page)` returns the next
    cursor; `None` ends iteration.
    """
    effective_chunk = chunk_size or 0
    user_limit = limit or 0

    first_limit = _min_for_limit_param(limit, effective_chunk)
    first_page = fetch_page(**{**kwargs, cursor_param: initial_cursor, 'limit': first_limit})

    def iterator() -> Iterator[Any]:
        current = first_page
        yield from current.items  # type: ignore[attr-defined]

        fetched = len(current.items)  # type: ignore[attr-defined]
        next_cursor = next_cursor_fn(current)

        while (
            current.items  # type: ignore[attr-defined]
            and next_cursor is not None
            and (not user_limit or user_limit > fetched)
        ):
            remaining = (user_limit - fetched) if user_limit else 0
            next_limit = effective_chunk if not user_limit else _min_for_limit_param(remaining, effective_chunk)
            current = fetch_page(**{**kwargs, cursor_param: next_cursor, 'limit': next_limit})
            yield from current.items  # type: ignore[attr-defined]
            fetched += len(current.items)  # type: ignore[attr-defined]
            next_cursor = next_cursor_fn(current)

    return factory(first_page, iterator())


def build_awaitable_async_iterable_offset(
    fetch_page: Callable[..., Awaitable[M]],
    **kwargs: Any,
) -> AwaitableAsyncIterable[M, Any]:
    """Build an offset-paginated async `Awaitable[M] + AsyncIterable[T]` result.

    `await` resolves to the raw typed first page (`ListOf*`); `async for` yields items across
    pages. No factory is needed on the async side — the typed `M` is returned directly.
    """
    chunk_size = kwargs.pop('chunk_size', 0) or 0
    offset = kwargs.get('offset') or 0
    limit = kwargs.get('limit') or 0

    async def fetch_first() -> M:
        return await fetch_page(**{**kwargs, 'limit': _min_for_limit_param(kwargs.get('limit'), chunk_size)})

    async def async_iterator() -> AsyncIterator[Any]:
        current = await fetch_first()
        for item in current.items:  # type: ignore[attr-defined]
            yield item

        fetched = len(current.items)  # type: ignore[attr-defined]
        while current.items and (not limit or (limit > fetched)):  # type: ignore[attr-defined]
            new_kwargs = {
                **kwargs,
                'offset': offset + fetched,
                'limit': chunk_size if not limit else _min_for_limit_param(limit - fetched, chunk_size),
            }
            current = await fetch_page(**new_kwargs)
            for item in current.items:  # type: ignore[attr-defined]
                yield item
            fetched += len(current.items)  # type: ignore[attr-defined]

    return AwaitableAsyncIterable(fetch_first, async_iterator())


def build_awaitable_async_iterable_cursor(
    fetch_page: Callable[..., Awaitable[M]],
    *,
    cursor_param: str,
    next_cursor_fn: Callable[[Any], Any],
    initial_cursor: Any = None,
    limit: int | None = None,
    chunk_size: int | None = None,
    **kwargs: Any,
) -> AwaitableAsyncIterable[M, Any]:
    """Async counterpart of `build_iterable_cursor`."""
    effective_chunk = chunk_size or 0
    user_limit = limit or 0
    first_limit = _min_for_limit_param(limit, effective_chunk)

    async def fetch_first() -> M:
        return await fetch_page(**{**kwargs, cursor_param: initial_cursor, 'limit': first_limit})

    async def async_iterator() -> AsyncIterator[Any]:
        current = await fetch_first()
        for item in current.items:  # type: ignore[attr-defined]
            yield item

        fetched = len(current.items)  # type: ignore[attr-defined]
        next_cursor = next_cursor_fn(current)

        while (
            current.items  # type: ignore[attr-defined]
            and next_cursor is not None
            and (not user_limit or user_limit > fetched)
        ):
            remaining = (user_limit - fetched) if user_limit else 0
            next_limit = effective_chunk if not user_limit else _min_for_limit_param(remaining, effective_chunk)
            current = await fetch_page(**{**kwargs, cursor_param: next_cursor, 'limit': next_limit})
            for item in current.items:  # type: ignore[attr-defined]
                yield item
            fetched += len(current.items)  # type: ignore[attr-defined]
            next_cursor = next_cursor_fn(current)

    return AwaitableAsyncIterable(fetch_first, async_iterator())


__all__ = [
    'AwaitableAsyncIterable',
    'IterableDatasetItemsPage',
    'IterableListOfActors',
    'IterableListOfBuilds',
    'IterableListOfDatasets',
    'IterableListOfEnvVars',
    'IterableListOfKeyValueStores',
    'IterableListOfKeys',
    'IterableListOfRequestQueues',
    'IterableListOfRequests',
    'IterableListOfRuns',
    'IterableListOfSchedules',
    'IterableListOfStoreActors',
    'IterableListOfTasks',
    'IterableListOfVersions',
    'IterableListOfWebhookDispatches',
    'IterableListOfWebhooks',
    'IterableListPage',
    'build_awaitable_async_iterable_cursor',
    'build_awaitable_async_iterable_offset',
    'build_iterable_cursor',
    'build_iterable_offset',
]
