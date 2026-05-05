from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, TypeVar, overload

from apify_client._models import KeyValueStoreKey, ListOfKeys, ListOfRequests, Request

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Awaitable, Callable, Iterator

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


def get_items_iterator(
    callback: Callable[..., HasItems[T]],
    *,
    limit: int | None = None,
    offset: int | None = None,
    chunk_size: int | None = None,
) -> Iterator[T]:
    """Yield individual items from offset-based paginated API responses.

    The `callback` is invoked lazily to fetch each page from the API. It must accept `limit` and
    `offset` keyword arguments and return an object whose `items` attribute is a list. If the
    object also exposes a `count` attribute, it is used for offset bookkeeping (the Apify API's
    `count` reflects items scanned, which can exceed items returned when filters are applied).

    Iteration stops when a page returns no items or when the user-requested `limit` is reached.
    The `total` field is intentionally not consulted, because it can change between calls.

    Args:
        callback: Function returning a single page of items.
        limit: Maximum total number of items to yield across all pages. `None` or `0` means no limit.
        offset: Starting offset for the first page.
        chunk_size: Maximum number of items requested per API call. `None` or `0` lets the API decide.
    """
    effective_chunk = chunk_size or 0
    initial_offset = offset or 0
    initial_limit = limit or 0
    fetched_items = 0

    while True:
        current_page = callback(
            limit=effective_chunk
            if not initial_limit
            else _min_for_limit_param(initial_limit - fetched_items, effective_chunk),
            offset=initial_offset + fetched_items,
        )
        yield from current_page.items

        fetched_items += getattr(current_page, 'count', len(current_page.items))

        if not current_page.items or (initial_limit and fetched_items >= initial_limit):
            break


async def get_items_iterator_async(
    callback: Callable[..., Awaitable[HasItems[T]]],
    *,
    limit: int | None = None,
    offset: int | None = None,
    chunk_size: int | None = None,
) -> AsyncIterator[T]:
    """Async variant of :func:`get_items_iterator`.

    The `callback` must be an awaitable returning a single page of items.
    """
    effective_chunk = chunk_size or 0
    initial_offset = offset or 0
    initial_limit = limit or 0
    fetched_items = 0

    while True:
        current_page = await callback(
            limit=effective_chunk
            if not initial_limit
            else _min_for_limit_param(initial_limit - fetched_items, effective_chunk),
            offset=initial_offset + fetched_items,
        )
        for item in current_page.items:
            yield item

        fetched_items += getattr(current_page, 'count', len(current_page.items))

        if not current_page.items or (initial_limit and fetched_items >= initial_limit):
            break


@overload
def get_cursor_iterator(
    callback: Callable[..., ListOfKeys],
    *,
    cursor: str | None = None,
    limit: int | None = None,
    chunk_size: int | None = None,
) -> Iterator[KeyValueStoreKey]: ...
@overload
def get_cursor_iterator(
    callback: Callable[..., ListOfRequests],
    *,
    cursor: str | None = None,
    limit: int | None = None,
    chunk_size: int | None = None,
) -> Iterator[Request]: ...


def get_cursor_iterator(
    callback: Callable[..., ListOfKeys] | Callable[..., ListOfRequests],
    *,
    cursor: str | None = None,
    limit: int | None = None,
    chunk_size: int | None = None,
) -> Iterator[Request] | Iterator[KeyValueStoreKey]:
    """Yield individual items from cursor-paginated API responses.

    Each page is expected to expose `items` and `next_<cursor_param>`; iteration ends when a
    page returns no items, the next cursor is `None`, or the user-requested `limit` is reached.

    Args:
        callback: Function returning a single page of items. Receives the cursor as a kwarg
            named after `cursor_param` and a `limit` kwarg.
        cursor_param: Name of the cursor query-parameter (e.g. `cursor` or `exclusive_start_key`).
        cursor: Value of the cursor for the first request, or `None` to start from the beginning.
        limit: Maximum total number of items to yield across all pages.
        chunk_size: Maximum number of items requested per API call.
    """
    effective_chunk = chunk_size or 0
    initial_limit = limit or 0
    fetched_items = 0

    while True:
        current_page = callback(
            limit=effective_chunk
            if not initial_limit
            else _min_for_limit_param(initial_limit - fetched_items, effective_chunk),
            cursor=cursor,
        )
        yield from current_page.items

        fetched_items += getattr(current_page, 'count', len(current_page.items))

        if isinstance(current_page, ListOfKeys):
            cursor = current_page.next_exclusive_start_key
        elif isinstance(current_page, ListOfRequests):
            cursor = current_page.next_cursor
        else:
            raise TypeError('Unsupported page type returned by callback; expected ListOfKeys or ListOfRequests.')

        if not current_page.items or cursor is None or (initial_limit and fetched_items >= initial_limit):
            break


@overload
def get_cursor_iterator_async(
    callback: Callable[..., Awaitable[ListOfKeys]],
    *,
    cursor: str | None = None,
    limit: int | None = None,
    chunk_size: int | None = None,
) -> AsyncIterator[KeyValueStoreKey]: ...
@overload
def get_cursor_iterator_async(
    callback: Callable[..., Awaitable[ListOfRequests]],
    *,
    cursor: str | None = None,
    limit: int | None = None,
    chunk_size: int | None = None,
) -> AsyncIterator[Request]: ...


async def get_cursor_iterator_async(
    callback: Callable[..., Awaitable[ListOfKeys]] | Callable[..., Awaitable[ListOfRequests]],
    *,
    cursor: str | None = None,
    limit: int | None = None,
    chunk_size: int | None = None,
) -> AsyncIterator[KeyValueStoreKey] | AsyncIterator[Request]:
    """Async variant of :func:`get_cursor_iterator`."""
    effective_chunk = chunk_size or 0
    initial_limit = limit or 0
    fetched_items = 0

    while True:
        current_page = await callback(
            limit=effective_chunk
            if not initial_limit
            else _min_for_limit_param(initial_limit - fetched_items, effective_chunk),
            cursor=cursor,
        )
        for item in current_page.items:
            yield item

        fetched_items += getattr(current_page, 'count', len(current_page.items))

        if isinstance(current_page, ListOfKeys):
            cursor = current_page.next_exclusive_start_key
        elif isinstance(current_page, ListOfRequests):
            cursor = current_page.next_cursor
        else:
            raise TypeError('Unsupported page type returned by callback; expected ListOfKeys or ListOfRequests.')

        if not current_page.items or cursor is None or (initial_limit and fetched_items >= initial_limit):
            break
