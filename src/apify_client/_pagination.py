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

    Implementations must expose `items`. They may optionally expose `count` - the number of rows the API scanned to
    produce this page, which `len(items)` can land below (filters drop items) or above (`unwind` splits one row into
    several items). The iterator helpers consult `count` opportunistically via `getattr` for offset bookkeeping and
    fall back to `len(items)` when it is absent.
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
    is used for offset bookkeeping - `_page_scanned_rows` describes how the next offset is derived.

    Iteration stops when a page scans no rows or when the user-requested `limit` is reached. A page can scan rows while
    returning no items - filters like `clean` drop items from `items` but still count toward `count` - so terminating on
    scanned rather than returned rows keeps the iterator advancing across fully-filtered pages. The `total` field is
    intentionally not consulted, because it can change between calls.

    Args:
        callback: Function returning a single page of items.
        limit: Maximum total number of rows scanned across all pages. On the dataset items endpoint `unwind` can
            turn one row into several items, so more items than this can be yielded. `None` or `0` means no limit.
        offset: Starting offset for the first page.
        chunk_size: Per-page cap, sent to the API as its `limit`. `None` or `0` lets the API decide.
    """
    effective_chunk = chunk_size or 0
    initial_offset = offset or 0
    initial_limit = limit or 0
    fetched_items = 0

    while True:
        page_limit = _next_page_limit(initial_limit, fetched_items, effective_chunk)
        current_page = callback(
            limit=page_limit,
            offset=initial_offset + fetched_items,
        )
        yield from current_page.items

        page_scanned = _page_scanned_rows(current_page, page_limit)
        fetched_items += page_scanned

        if not page_scanned or (initial_limit and fetched_items >= initial_limit):
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
        page_limit = _next_page_limit(initial_limit, fetched_items, effective_chunk)
        current_page = await callback(
            limit=page_limit,
            offset=initial_offset + fetched_items,
        )
        for item in current_page.items:
            yield item

        page_scanned = _page_scanned_rows(current_page, page_limit)
        fetched_items += page_scanned

        if not page_scanned or (initial_limit and fetched_items >= initial_limit):
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
    `ListOfRequests` (for request queue requests). Iteration ends when the next cursor is `None` or the user-requested
    `limit` is reached. An empty page does not end it by itself, and it does not need to: both endpoints send a next
    cursor only alongside a page that has items. The key-value store's cursor is the last key of the page it just
    returned, and the request queue sends one only for a page that came back full, so an empty page always arrives with
    a `None` cursor.

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

        fetched_items += len(current_page.items)
        cursor = (
            current_page.next_exclusive_start_key if isinstance(current_page, ListOfKeys) else current_page.next_cursor
        )

        if cursor is None or (initial_limit and fetched_items >= initial_limit):
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

        fetched_items += len(current_page.items)
        cursor = (
            current_page.next_exclusive_start_key if isinstance(current_page, ListOfKeys) else current_page.next_cursor
        )

        if cursor is None or (initial_limit and fetched_items >= initial_limit):
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


def _page_scanned_rows(page: HasItems[T], requested_limit: int) -> int:
    """Compute how far the offset advances past `page`, in dataset rows.

    Neither reported number is right on its own. `count` follows the rows the API scanned, but it is derived from a
    dataset's item count, which is incremented by a throttled write and so lags a fresh push. `len(items)` counts the
    items the API shaped out of those rows: filters (`clean`, `skip_empty`, `skip_hidden`) drop some, and `unwind`
    splits one row into several. The larger of the two absorbs a `count` that lags behind the items returned, and
    capping it at the rows the call asked for keeps an unwound page from advancing past rows the next call would then
    never read. The cap is a valid bound because the endpoint applies the `limit` it is sent verbatim; on a page
    covering fewer rows than that, the advance can still overshoot into rows a concurrent push appends afterwards. A
    `requested_limit` of `0` means the call sent no limit, leaving the advance unbounded.
    """
    scanned_rows = max(getattr(page, 'count', 0), len(page.items))
    return min(scanned_rows, requested_limit) if requested_limit else scanned_rows
