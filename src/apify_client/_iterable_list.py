"""Primitives for list methods that are simultaneously a typed page and an iterator across pages.

Aligned with the JS client's `Promise<Result> & AsyncIterable<Item>` pattern
(see apify/apify-client-js#803).

**Sync return type**: a subclass of the existing Pydantic `ListOf*` model that additionally
implements `__iter__`, yielding individual items across pages. For example,
`IterableListOfWebhooks` is a `ListOfWebhooks` that also satisfies `Iterable[WebhookShort]`.
`isinstance(result, ListOfWebhooks)` is `True`, `.items` / `.total` / `.count` remain typed
access to the first page's metadata, and `for w in result` iterates individual webhooks across
pages (automatically fetching subsequent pages).

**Async return type**: a generic `AwaitableAsyncIterable[M, T]` that is simultaneously
`Awaitable[M]` (`await` resolves to the first page as a typed model) and `AsyncIterable[T]`
(`async for` iterates individual items across pages).
"""

from __future__ import annotations

from collections.abc import AsyncIterable, AsyncIterator, Awaitable, Callable, Generator, Iterator
from typing import Any, Generic, Protocol, TypeVar

from pydantic import PrivateAttr

from apify_client._docs import docs_group
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

M = TypeVar('M')
T = TypeVar('T')


class _PageLike(Protocol):
    """Minimal structural type that the builders need from a page object."""

    items: list[Any]


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
# Sync: per-model `Iterable` subclasses. Each `IterableListOfX` IS a `ListOfX`
# (so `isinstance`, typed field access, `.items`, `.total`, etc. all work) AND
# structurally satisfies `Iterable[ItemType]` via an overridden `__iter__`.
#
# `PrivateAttr` stores the page-crossing iterator. When unset (e.g. a plain
# `ListOfX.model_validate(...)` that was upgraded to an `IterableListOfX`),
# `__iter__` falls back to iterating the first page's `.items`.
# ---------------------------------------------------------------------------


@docs_group('Other')
class IterableListOfActors(ListOfActors):
    """A `ListOfActors` that is also `Iterable[ActorShort]` across pages."""

    _iter_impl: Iterator[ActorShort] | None = PrivateAttr(default=None)

    def __iter__(self) -> Iterator[ActorShort]:  # ty: ignore[invalid-method-override]
        return self._iter_impl if self._iter_impl is not None else iter(self.items)


@docs_group('Other')
class IterableListOfBuilds(ListOfBuilds):
    """A `ListOfBuilds` that is also `Iterable[BuildShort]` across pages."""

    _iter_impl: Iterator[BuildShort] | None = PrivateAttr(default=None)

    def __iter__(self) -> Iterator[BuildShort]:  # ty: ignore[invalid-method-override]
        return self._iter_impl if self._iter_impl is not None else iter(self.items)


@docs_group('Other')
class IterableListOfDatasets(ListOfDatasets):
    """A `ListOfDatasets` that is also `Iterable[DatasetListItem]` across pages."""

    _iter_impl: Iterator[DatasetListItem] | None = PrivateAttr(default=None)

    def __iter__(self) -> Iterator[DatasetListItem]:  # ty: ignore[invalid-method-override]
        return self._iter_impl if self._iter_impl is not None else iter(self.items)


@docs_group('Other')
class IterableListOfEnvVars(ListOfEnvVars):
    """A `ListOfEnvVars` that is also `Iterable[EnvVar]` across pages."""

    _iter_impl: Iterator[EnvVar] | None = PrivateAttr(default=None)

    def __iter__(self) -> Iterator[EnvVar]:  # ty: ignore[invalid-method-override]
        return self._iter_impl if self._iter_impl is not None else iter(self.items)


@docs_group('Other')
class IterableListOfKeyValueStores(ListOfKeyValueStores):
    """A `ListOfKeyValueStores` that is also `Iterable[KeyValueStore]` across pages."""

    _iter_impl: Iterator[KeyValueStore] | None = PrivateAttr(default=None)

    def __iter__(self) -> Iterator[KeyValueStore]:  # ty: ignore[invalid-method-override]
        return self._iter_impl if self._iter_impl is not None else iter(self.items)


@docs_group('Other')
class IterableListOfKeys(ListOfKeys):
    """A `ListOfKeys` that is also `Iterable[KeyValueStoreKey]` across pages."""

    _iter_impl: Iterator[KeyValueStoreKey] | None = PrivateAttr(default=None)

    def __iter__(self) -> Iterator[KeyValueStoreKey]:  # ty: ignore[invalid-method-override]
        return self._iter_impl if self._iter_impl is not None else iter(self.items)


@docs_group('Other')
class IterableListOfRequestQueues(ListOfRequestQueues):
    """A `ListOfRequestQueues` that is also `Iterable[RequestQueueShort]` across pages."""

    _iter_impl: Iterator[RequestQueueShort] | None = PrivateAttr(default=None)

    def __iter__(self) -> Iterator[RequestQueueShort]:  # ty: ignore[invalid-method-override]
        return self._iter_impl if self._iter_impl is not None else iter(self.items)


@docs_group('Other')
class IterableListOfRequests(ListOfRequests):
    """A `ListOfRequests` that is also `Iterable[Request]` across pages."""

    _iter_impl: Iterator[Request] | None = PrivateAttr(default=None)

    def __iter__(self) -> Iterator[Request]:  # ty: ignore[invalid-method-override]
        return self._iter_impl if self._iter_impl is not None else iter(self.items)


@docs_group('Other')
class IterableListOfRuns(ListOfRuns):
    """A `ListOfRuns` that is also `Iterable[RunShort]` across pages."""

    _iter_impl: Iterator[RunShort] | None = PrivateAttr(default=None)

    def __iter__(self) -> Iterator[RunShort]:  # ty: ignore[invalid-method-override]
        return self._iter_impl if self._iter_impl is not None else iter(self.items)


@docs_group('Other')
class IterableListOfSchedules(ListOfSchedules):
    """A `ListOfSchedules` that is also `Iterable[ScheduleShort]` across pages."""

    _iter_impl: Iterator[ScheduleShort] | None = PrivateAttr(default=None)

    def __iter__(self) -> Iterator[ScheduleShort]:  # ty: ignore[invalid-method-override]
        return self._iter_impl if self._iter_impl is not None else iter(self.items)


@docs_group('Other')
class IterableListOfStoreActors(ListOfStoreActors):
    """A `ListOfStoreActors` that is also `Iterable[StoreListActor]` across pages."""

    _iter_impl: Iterator[StoreListActor] | None = PrivateAttr(default=None)

    def __iter__(self) -> Iterator[StoreListActor]:  # ty: ignore[invalid-method-override]
        return self._iter_impl if self._iter_impl is not None else iter(self.items)


@docs_group('Other')
class IterableListOfTasks(ListOfTasks):
    """A `ListOfTasks` that is also `Iterable[TaskShort]` across pages."""

    _iter_impl: Iterator[TaskShort] | None = PrivateAttr(default=None)

    def __iter__(self) -> Iterator[TaskShort]:  # ty: ignore[invalid-method-override]
        return self._iter_impl if self._iter_impl is not None else iter(self.items)


@docs_group('Other')
class IterableListOfVersions(ListOfVersions):
    """A `ListOfVersions` that is also `Iterable[Version]` across pages."""

    _iter_impl: Iterator[Version] | None = PrivateAttr(default=None)

    def __iter__(self) -> Iterator[Version]:  # ty: ignore[invalid-method-override]
        return self._iter_impl if self._iter_impl is not None else iter(self.items)


@docs_group('Other')
class IterableListOfWebhookDispatches(ListOfWebhookDispatches):
    """A `ListOfWebhookDispatches` that is also `Iterable[WebhookDispatch]` across pages."""

    _iter_impl: Iterator[WebhookDispatch] | None = PrivateAttr(default=None)

    def __iter__(self) -> Iterator[WebhookDispatch]:  # ty: ignore[invalid-method-override]
        return self._iter_impl if self._iter_impl is not None else iter(self.items)


@docs_group('Other')
class IterableListOfWebhooks(ListOfWebhooks):
    """A `ListOfWebhooks` that is also `Iterable[WebhookShort]` across pages."""

    _iter_impl: Iterator[WebhookShort] | None = PrivateAttr(default=None)

    def __iter__(self) -> Iterator[WebhookShort]:  # ty: ignore[invalid-method-override]
        return self._iter_impl if self._iter_impl is not None else iter(self.items)


# ---------------------------------------------------------------------------
# Async: a single generic `Awaitable[M] & AsyncIterable[T]`.
# ---------------------------------------------------------------------------


@docs_group('Other')
class AwaitableAsyncIterable(AsyncIterable[T], Generic[M, T]):
    """A value that is both `Awaitable[M]` and `AsyncIterable[T]`.

    Mirrors the JS `Promise<Result> & AsyncIterable<Item>` pattern: callers can `await` the
    value to get `M` (the first page as a typed Pydantic model), or `async for item in ...` to
    iterate individual items of type `T` across pages.

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
# Builder helpers. The callback returns an already-typed `IterableListOfX`
# instance; the builder only arranges pagination and attaches the iterator.
# ---------------------------------------------------------------------------


def _attach_iterator(instance: Any, iterator: Iterator[Any]) -> Any:
    """Assign the page-crossing iterator to the instance's `_iter_impl` private attribute."""
    instance._iter_impl = iterator  # noqa: SLF001
    return instance


IterableListT = TypeVar('IterableListT', bound=_PageLike)


def build_iterable_offset(callback: Callable[..., IterableListT], **kwargs: Any) -> IterableListT:
    """Build an offset-paginated, sync iterable result.

    The callback is invoked with `{offset, limit, **kwargs}` and must return an
    `IterableListOfX` instance (populated from the API response). Iteration stops when a page
    is empty or the caller-supplied `limit` is reached.
    """
    chunk_size = kwargs.pop('chunk_size', 0) or 0
    offset = kwargs.get('offset') or 0
    limit = kwargs.get('limit') or 0

    first_page: Any = callback(**{**kwargs, 'limit': _min_for_limit_param(kwargs.get('limit'), chunk_size)})

    def iterator() -> Iterator[Any]:
        current_page = first_page
        yield from current_page.items

        fetched = len(current_page.items)
        while current_page.items and (not limit or (limit > fetched)):
            new_kwargs = {
                **kwargs,
                'offset': offset + fetched,
                'limit': chunk_size if not limit else _min_for_limit_param(limit - fetched, chunk_size),
            }
            current_page = callback(**new_kwargs)
            yield from current_page.items
            fetched += len(current_page.items)

    return _attach_iterator(first_page, iterator())


def build_awaitable_async_iterable_offset(
    callback: Callable[..., Awaitable[IterableListT]],
    **kwargs: Any,
) -> AwaitableAsyncIterable[IterableListT, Any]:
    """Build an offset-paginated, async `Awaitable + AsyncIterable` result.

    `await` resolves to the first page as the typed `IterableListOfX` returned by the callback
    (so callers retain full typed-field access). `async for` iterates items across pages.
    """
    chunk_size = kwargs.pop('chunk_size', 0) or 0
    offset = kwargs.get('offset') or 0
    limit = kwargs.get('limit') or 0

    async def fetch_first() -> Any:
        return await callback(**{**kwargs, 'limit': _min_for_limit_param(kwargs.get('limit'), chunk_size)})

    async def async_iterator() -> AsyncIterator[Any]:
        current_page = await fetch_first()
        for item in current_page.items:
            yield item

        fetched = len(current_page.items)
        while current_page.items and (not limit or (limit > fetched)):
            new_kwargs = {
                **kwargs,
                'offset': offset + fetched,
                'limit': chunk_size if not limit else _min_for_limit_param(limit - fetched, chunk_size),
            }
            current_page = await callback(**new_kwargs)
            for item in current_page.items:
                yield item
            fetched += len(current_page.items)

    return AwaitableAsyncIterable(fetch_first, async_iterator())


def build_iterable_cursor(
    callback: Callable[..., IterableListT],
    *,
    cursor_param: str,
    next_cursor_fn: Callable[[Any], Any],
    initial_cursor: Any = None,
    limit: int | None = None,
    chunk_size: int | None = None,
    **kwargs: Any,
) -> IterableListT:
    """Build a cursor-paginated, sync iterable result.

    Analogous to `build_iterable_offset`, but pagination uses a cursor: the callback is called
    with `{cursor_param: cursor, limit, **kwargs}`. `next_cursor_fn(page)` returns the next
    cursor; `None` ends iteration.
    """
    effective_chunk = chunk_size or 0
    user_limit = limit or 0

    first_limit = _min_for_limit_param(limit, effective_chunk)
    first_page: Any = callback(**{**kwargs, cursor_param: initial_cursor, 'limit': first_limit})

    def iterator() -> Iterator[Any]:
        current_page = first_page
        yield from current_page.items

        fetched = len(current_page.items)
        next_cursor = next_cursor_fn(current_page)

        while current_page.items and next_cursor is not None and (not user_limit or user_limit > fetched):
            remaining = (user_limit - fetched) if user_limit else 0
            next_limit = effective_chunk if not user_limit else _min_for_limit_param(remaining, effective_chunk)
            current_page = callback(**{**kwargs, cursor_param: next_cursor, 'limit': next_limit})
            yield from current_page.items
            fetched += len(current_page.items)
            next_cursor = next_cursor_fn(current_page)

    return _attach_iterator(first_page, iterator())


def build_awaitable_async_iterable_cursor(
    callback: Callable[..., Awaitable[IterableListT]],
    *,
    cursor_param: str,
    next_cursor_fn: Callable[[Any], Any],
    initial_cursor: Any = None,
    limit: int | None = None,
    chunk_size: int | None = None,
    **kwargs: Any,
) -> AwaitableAsyncIterable[IterableListT, Any]:
    """Async counterpart of `build_iterable_cursor`."""
    effective_chunk = chunk_size or 0
    user_limit = limit or 0
    first_limit = _min_for_limit_param(limit, effective_chunk)

    async def fetch_first() -> Any:
        return await callback(**{**kwargs, cursor_param: initial_cursor, 'limit': first_limit})

    async def async_iterator() -> AsyncIterator[Any]:
        current_page = await fetch_first()
        for item in current_page.items:
            yield item

        fetched = len(current_page.items)
        next_cursor = next_cursor_fn(current_page)

        while current_page.items and next_cursor is not None and (not user_limit or user_limit > fetched):
            remaining = (user_limit - fetched) if user_limit else 0
            next_limit = effective_chunk if not user_limit else _min_for_limit_param(remaining, effective_chunk)
            current_page = await callback(**{**kwargs, cursor_param: next_cursor, 'limit': next_limit})
            for item in current_page.items:
                yield item
            fetched += len(current_page.items)
            next_cursor = next_cursor_fn(current_page)

    return AwaitableAsyncIterable(fetch_first, async_iterator())


__all__ = [
    'AwaitableAsyncIterable',
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
    'build_awaitable_async_iterable_cursor',
    'build_awaitable_async_iterable_offset',
    'build_iterable_cursor',
    'build_iterable_offset',
]
