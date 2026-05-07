from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, TypeVar, overload

from apify_client._models import KeyValueStoreKey, ListOfKeys, ListOfRequests, Request

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Awaitable, Callable, Iterator

T = TypeVar('T')

DEFAULT_CHUNK_SIZE = 1000
"""Default per-page size used by the iterate helpers when the caller does not specify one.

The value of 1000 keeps backwards compatibility with the previous fixed cache size.
"""


class HasItems(Protocol[T]):
    """Structural contract for a single page of results from a paginated API endpoint.

    Implementations must expose `items`. They may optionally expose `count` — the number of items scanned by the API for
    this page, which can exceed `len(items)` when filters drop items from the response. The iterator helpers consult
    `count` opportunistically via `getattr` for offset bookkeeping and fall back to `len(items)` when it is absent.
    """

    items: list[T]


def get_items_iterator(
    callback: Callable[..., HasItems[T]],
    *,
    limit: int | None = None,
    offset: int | None = None,
    chunk_size: int | None = None,
) -> Iterator[T]:
    """Yield individual items from offset-based paginated API responses.

    The `callback` is invoked lazily to fetch each page from the API. It must accept `limit` and `offset` keyword
    arguments and return an object whose `items` attribute is a list. If the object also exposes a `count` attribute, it
    is used for offset bookkeeping (the Apify API's `count` reflects items scanned, which can exceed items returned when
    filters are applied).

    Iteration stops when a page returns no items or when the user-requested `limit` is reached. The `total` field is
    intentionally not consulted, because it can change between calls.

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
            limit=_next_page_limit(initial_limit, fetched_items, effective_chunk),
            offset=initial_offset + fetched_items,
        )
        yield from current_page.items

        fetched_items += max(getattr(current_page, 'count', 0), len(current_page.items))

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
            limit=_next_page_limit(initial_limit, fetched_items, effective_chunk),
            offset=initial_offset + fetched_items,
        )
        for item in current_page.items:
            yield item

        fetched_items += max(getattr(current_page, 'count', 0), len(current_page.items))

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
    callback: Callable[..., ListOfKeys | ListOfRequests],
    *,
    cursor: str | None = None,
    limit: int | None = None,
    chunk_size: int | None = None,
) -> Iterator[KeyValueStoreKey] | Iterator[Request]:
    """Yield individual items from cursor-paginated API responses.

    Cursor pagination is restricted to the two API responses that expose it: `ListOfKeys` (for key-value store keys) and
    `ListOfRequests` (for request queue requests). Iteration ends when a page returns no items, the next cursor is
    `None`, or the user-requested `limit` is reached.

    Args:
        callback: Function returning a single page of items. Receives `cursor` and `limit` kwargs.
        cursor: Value of the cursor for the first request, or `None` to start from the beginning.
        limit: Maximum total number of items to yield across all pages.
        chunk_size: Maximum number of items requested per API call.
    """
    effective_chunk = chunk_size or 0
    initial_limit = limit or 0
    fetched_items = 0

    while True:
        current_page = callback(
            limit=_next_page_limit(initial_limit, fetched_items, effective_chunk),
            cursor=cursor,
        )
        yield from current_page.items

        fetched_items += max(getattr(current_page, 'count', 0), len(current_page.items))
        cursor = (
            current_page.next_exclusive_start_key if isinstance(current_page, ListOfKeys) else current_page.next_cursor
        )

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
    callback: Callable[..., Awaitable[ListOfKeys | ListOfRequests]],
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
            limit=_next_page_limit(initial_limit, fetched_items, effective_chunk),
            cursor=cursor,
        )
        for item in current_page.items:
            yield item

        fetched_items += max(getattr(current_page, 'count', 0), len(current_page.items))
        cursor = (
            current_page.next_exclusive_start_key if isinstance(current_page, ListOfKeys) else current_page.next_cursor
        )

        if not current_page.items or cursor is None or (initial_limit and fetched_items >= initial_limit):
            break


def _next_page_limit(initial_limit: int, fetched_items: int, effective_chunk: int) -> int:
    """Compute the `limit` value for the next API call.

    `0` means no limit on the wire (matches the Apify API contract). When both an overall `initial_limit` and a per-page
    `effective_chunk` are set, the call is clamped to whichever is smaller; if either is unset (`0`), the other wins.
    """
    if not initial_limit:
        return effective_chunk
    remaining = initial_limit - fetched_items
    if not effective_chunk:
        return remaining
    return min(remaining, effective_chunk)
