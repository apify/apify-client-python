from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any, Generic, Protocol, TypeVar

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Awaitable, Callable, Coroutine, Generator, Iterator

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


def get_items_iterator(
    callback: Callable[..., HasItems[T]],
    limit: int | None = None,
    offset: int | None = None,
    chunk_size: int | None = None,
) -> Iterator[T]:
    """Yield individual items from paginated API responses.

    The callback is invoked to lazy fetch items from API.

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
    chunk_size = chunk_size or 0
    initial_offset = offset or 0
    limit = limit or 0
    fetched_items = 0

    while True:
        current_page = callback(
            limit=chunk_size if not limit else _min_for_limit_param(limit - fetched_items, chunk_size),
            offset=initial_offset + fetched_items
        )
        yield from current_page.items
        fetched_items += getattr(current_page, 'count', len(current_page.items))

        if not current_page.items or (limit and fetched_items >= limit):
            break


def build_get_iterator(
    callback: Callable[..., HasItems[T]],
    first_page: HasItems[T],
    **kwargs: Any,
) -> Callable[[], Iterator[T]]:
    """Build a factory for `Iterator` to yield items across paginated API calls.

    The callback is invoked to lazy fetch items from API.

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

    return get_iterator


def build_get_iterator_async(
    callback: Callable[..., Coroutine[Any, Any, HasItems[T]]],
    fetch_first_page: Awaitable[HasItems[T]],
    **kwargs: Any,
) -> Callable[[], AsyncIterator[T]]:
    """Build a factory for `AsyncIterator` to yield items across paginated API calls.

    Mirrors `build_get_iterator` but for async callbacks.
    """
    chunk_size = kwargs.pop('chunk_size', 0) or 0
    offset = kwargs.get('offset') or 0
    limit = kwargs.get('limit') or 0

    async def get_async_iterator() -> AsyncIterator[T]:
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

    return get_async_iterator


def build_get_cursor_iterator(
    callback: Callable[..., HasItems[T]],
    first_page: HasItems[T],
    *,
    cursor_param: str,
    limit: int | None = None,
    chunk_size: int | None = None,
    **kwargs: Any,
) -> Callable[[], Iterator[T]]:
    """Build a factory for `Iterator` to yield items across paginated API calls.

    Mirrors `build_get_iterator` but with cursor based pagination.

    The caller is responsible for fetching the first page (typically by calling `callback` with
    the initial cursor). After each page, `getattr(page, f'next_{cursor_param}')` is consulted
    to obtain the next cursor; returning `None` ends iteration. The iteration also stops when a
    page is empty or when the caller-requested `limit` has been reached.
    """
    effective_chunk = chunk_size or 0
    user_limit = limit or 0

    def get_iterator() -> Iterator[T]:
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

    return get_iterator


def build_get_cursor_iterator_async(
    callback: Callable[..., Coroutine[Any, Any, HasItems[T]]],
    fetch_first_page: Awaitable[HasItems[T]],
    *,
    cursor_param: str,
    limit: int | None = None,
    chunk_size: int | None = None,
    **kwargs: Any,
) -> Callable[[], AsyncIterator[T]]:
    """Build a factory for `Iterator` to yield items across paginated API calls.

    Mirrors `build_get_cursor_iterator` but for async callbacks.
    """
    effective_chunk = chunk_size or 0
    user_limit = limit or 0

    async def get_async_iterator() -> AsyncIterator[T]:
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

    return get_async_iterator
