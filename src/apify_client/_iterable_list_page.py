from __future__ import annotations

import asyncio
from collections.abc import AsyncIterable, AsyncIterator, Awaitable, Callable, Coroutine, Generator, Iterable, Iterator
from typing import Any, Generic, Protocol, TypeVar

from apify_client._docs import docs_group

T = TypeVar('T')


class HasItems(Protocol[T]):
    items: list[T]


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


class _LazyTask(Generic[T]):
    """Task that is created lazily upon awaiting.

    This allows to reuse the same Task multiple times without the need to schedule the task when it is created.
    """

    def __init__(self, awaitable: Coroutine[Any, Any, T]) -> None:
        self._awaitable = awaitable
        self._task: asyncio.Task[T] | None = None

    def __await__(self) -> Generator[Any, None, T]:
        if self._task is None:
            self._task = asyncio.create_task(self._awaitable)
        return (yield from self._task.__await__())


@docs_group('Other')
class ListPage(Generic[T]):
    """A page of API results.

    Different endpoints may return different subsets of the available pagination metadata fields, the only field that
    is common for all endpoints is items.
    """

    items: list[T]
    """List of items on this page."""

    count: int | None
    """Number of items on this page."""

    offset: int | None
    """The starting offset of this page."""

    limit: int | None
    """The maximum number of items per page requested from the API."""

    total: int | None
    """Total number of items matching the query, as reported by the first page."""

    desc: bool | None
    """Whether the items are sorted in descending order."""

    def __init__(self, first_page: HasItems[T]) -> None:
        """Initialize a page wrapper from a Pydantic paginated model."""
        self.items = first_page.items
        self.count = getattr(first_page, 'count', None)
        self.offset = getattr(first_page, 'offset', None)
        self.limit = getattr(first_page, 'limit', None)
        self.total = getattr(first_page, 'total', None)
        self.desc = getattr(first_page, 'desc', None)


@docs_group('Other')
class IterableListPage(ListPage[T], Iterable[T], Generic[T]):
    """A page of results that can also be iterated to yield items across subsequent pages.

    Accessing fields such as `items`, `count`, or `total` returns the metadata of the first page,
    preserving the behavior of the previous non-iterable return value. Iterating with `for item in ...`
    yields individual items and performs additional API calls as needed to fetch further pages.
    """

    def __init__(self, first_page: HasItems[T], get_iterator: Callable[[], Iterator[T]]) -> None:
        """Initialize a page wrapper from a Pydantic paginated model and an iterator over all items."""
        super().__init__(first_page)
        self._get_iterator = get_iterator

    def __iter__(self) -> Iterator[T]:
        """Return an iterator over all items across pages, fetching additional pages as needed."""
        return self._get_iterator()


@docs_group('Other')
class IterableListPageAsync(AsyncIterable[T], Generic[T]):
    """An awaitable result that can also be asynchronously iterated to yield items across pages.

    Awaiting the instance (`await client.list(...)`) performs a single API call and returns a
    populated `ListPage`. Iterating (`async for item in client.list(...)`) yields individual
    items and performs additional API calls as needed to fetch further pages.
    """

    def __init__(
        self,
        awaitable_first_page: Callable[[], Awaitable[ListPage[T]]],
        get_async_iterator: Callable[[], AsyncIterator[T]],
    ) -> None:
        """Initialize with a factory that creates the awaitable on demand and the async iterator over items."""
        self._awaitable_first_page = awaitable_first_page
        self._get_async_iterator = get_async_iterator

    def __aiter__(self) -> AsyncIterator[T]:
        """Return an asynchronous iterator over all items across pages."""
        return self._get_async_iterator()

    def __await__(self) -> Generator[Any, Any, ListPage[T]]:
        """Return an awaitable that resolves to an `IterableListPage` containing the first page."""
        return self._awaitable_first_page().__await__()


def build_iterable_list_page(
    callback: Callable[..., HasItems[T]],
    **kwargs: Any,
) -> IterableListPage[T]:
    """Build an `IterableListPage` from a paginated sync callback.

    The callback is invoked once immediately to fetch the first page, and again lazily during
    iteration to fetch further pages.

    There are several optional kwargs that control the pagination, but not all are accepted on each paginated endpoint.
    Some endpoints do not return all paginated metadata, so the implementation should be resilient to missing fields,
    but it can use them if available.

    The `total` field from the first page is not trusted for stopping iteration because it may change between calls;
    iteration stops when a page has no items or when the user-requested `limit` has been reached.

    The `count` field does not count objects returned, but objects scanned by the API. For example when using filters,
    returned items can be smaller than `count`. Therefore, `count` should be used for correct offset calculation if
    available.

    Iteration relevant kwargs:
        chunk_size: Maximum number of items requested per API call during iteration. Pass `0`
            or `None` to let the API decide (effectively infinity).
        limit: User-requested total item limit. Stops iteration once this many items are yielded.
        offset: Starting offset for the first page.
        **other: Passed through to the callback unchanged.
    """
    chunk_size = kwargs.pop('chunk_size', 0) or 0
    offset = kwargs.get('offset') or 0
    limit = kwargs.get('limit') or 0

    first_page = callback(**{**kwargs, 'limit': _min_for_limit_param(kwargs.get('limit'), chunk_size)})

    def get_iterator() -> Iterator[T]:
        current_page = first_page
        yield from current_page.items

        fetched_items = getattr(current_page, 'count', len(current_page.items))
        while current_page.items and (not limit or (limit > fetched_items)):
            new_kwargs = {
                **kwargs,
                'offset': offset + fetched_items,
                'limit': chunk_size if not limit else _min_for_limit_param(limit - fetched_items, chunk_size),
            }
            current_page = callback(**new_kwargs)
            yield from current_page.items
            fetched_items += getattr(current_page, 'count', len(current_page.items))

    return IterableListPage(first_page, get_iterator)


def build_iterable_list_page_async(
    callback: Callable[..., Coroutine[Any, Any, HasItems[T]]],
    **kwargs: Any,
) -> IterableListPageAsync[T]:
    """Build an `IterableListPageAsync` from a paginated async callback.

    Mirrors `build_iterable_list_page` but for async callbacks. The returned object is both
    awaitable (resolves to the first page wrapped in `IterableListPage`) and asynchronously
    iterable (yields items across pages).
    """
    chunk_size = kwargs.pop('chunk_size', 0) or 0
    offset = kwargs.get('offset') or 0
    limit = kwargs.get('limit') or 0

    # Can be awaited multiple times with same result, but not scheduled at this time yet, as it might be pre-emptive.
    fetch_first_page = _LazyTask(callback(**{**kwargs, 'limit': _min_for_limit_param(kwargs.get('limit'), chunk_size)}))

    async def get_async_iterator() -> AsyncIterator[Any]:
        current_page = await fetch_first_page
        for item in current_page.items:
            yield item

        fetched_items = getattr(current_page, 'count', len(current_page.items))
        while current_page.items and (not limit or (limit > fetched_items)):
            new_kwargs = {
                **kwargs,
                'offset': offset + fetched_items,
                'limit': chunk_size if not limit else _min_for_limit_param(limit - fetched_items, chunk_size),
            }
            current_page = await callback(**new_kwargs)
            for item in current_page.items:
                yield item
            fetched_items += getattr(current_page, 'count', len(current_page.items))

    async def wrap_first_page() -> ListPage[Any]:
        first_page = await fetch_first_page
        return ListPage(first_page)

    return IterableListPageAsync(wrap_first_page, get_async_iterator)


def build_cursor_iterable_list_page(
    callback: Callable[..., HasItems[T]],
    *,
    cursor_param: str,
    initial_cursor: Any = None,
    limit: int | None = None,
    chunk_size: int | None = None,
    **kwargs: Any,
) -> IterableListPage[T]:
    """Build an `IterableListPage` for endpoints that paginate with a cursor instead of an offset.

    The callback is invoked with `{cursor_param: cursor, 'limit': effective_limit, **kwargs}` for each
    page, starting from `initial_cursor`. After each page, `next_cursor_fn(page)` is consulted to
    obtain the next cursor; returning `None` ends iteration. The iteration also stops when a page is
    empty or when the caller-requested `limit` has been reached.
    """
    effective_chunk = chunk_size or 0
    user_limit = limit or 0

    first_limit = _min_for_limit_param(limit, effective_chunk)
    first_page = callback(**{**kwargs, cursor_param: initial_cursor, 'limit': first_limit})

    def get_iterator() -> Iterator[Any]:
        current_page = first_page
        yield from current_page.items

        fetched = len(current_page.items)
        next_cursor = getattr(current_page, f'next_{cursor_param}')

        while current_page.items and next_cursor is not None and (not user_limit or user_limit > fetched):
            remaining = (user_limit - fetched) if user_limit else 0
            next_limit = effective_chunk if not user_limit else _min_for_limit_param(remaining, effective_chunk)
            current_page = callback(**{**kwargs, cursor_param: next_cursor, 'limit': next_limit})
            yield from current_page.items
            fetched += len(current_page.items)
            next_cursor = getattr(current_page, f'next_{cursor_param}')

    return IterableListPage(first_page, get_iterator)


def build_cursor_iterable_list_page_async(
    callback: Callable[..., Coroutine[Any, Any, HasItems[T]]],
    *,
    cursor_param: str,
    initial_cursor: Any = None,
    limit: int | None = None,
    chunk_size: int | None = None,
    **kwargs: Any,
) -> IterableListPageAsync[T]:
    """Build an `IterableListPageAsync` for endpoints that paginate with a cursor instead of an offset.

    Mirrors `build_cursor_iterable_list_page` but for async callbacks. The returned object is both
    awaitable (resolves to the first page wrapped in `IterableListPage`) and asynchronously iterable
    (yields items across pages using the supplied cursor strategy).
    """
    effective_chunk = chunk_size or 0
    user_limit = limit or 0
    first_limit = _min_for_limit_param(limit, effective_chunk)

    # Can be awaited multiple times with same result, but not scheduled at this time yet, as it might be pre-emptive.
    fetch_first_page = _LazyTask(callback(**{**kwargs, cursor_param: initial_cursor, 'limit': first_limit}))

    async def get_async_iterator() -> AsyncIterator[Any]:
        current_page = await fetch_first_page
        for item in current_page.items:
            yield item

        fetched = len(current_page.items)
        next_cursor = getattr(current_page, f'next_{cursor_param}')

        while current_page.items and next_cursor is not None and (not user_limit or user_limit > fetched):
            remaining = (user_limit - fetched) if user_limit else 0
            next_limit = effective_chunk if not user_limit else _min_for_limit_param(remaining, effective_chunk)
            current_page = await callback(**{**kwargs, cursor_param: next_cursor, 'limit': next_limit})
            for item in current_page.items:
                yield item
            fetched += len(current_page.items)
            next_cursor = getattr(current_page, f'next_{cursor_param}')

    async def wrap_first_page() -> ListPage[Any]:
        return ListPage(await fetch_first_page)

    return IterableListPageAsync(wrap_first_page, get_async_iterator)
