from __future__ import annotations

from collections.abc import AsyncIterable, AsyncIterator, Awaitable, Callable, Generator, Iterable, Iterator
from typing import Any, Generic, TypeVar

from apify_client._docs import docs_group

T = TypeVar('T')


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


@docs_group('Other')
class IterableListPage(Iterable[T], Generic[T]):
    """A page of results that can also be iterated to yield items across subsequent pages.

    Accessing fields such as `items`, `count`, or `total` returns the metadata of the first page,
    preserving the behavior of the previous non-iterable return value. Iterating with `for item in ...`
    yields individual items and performs additional API calls as needed to fetch further pages.
    """

    items: list[T]
    """List of items on this page."""

    count: int
    """Number of items on this page."""

    offset: int
    """The starting offset of this page."""

    limit: int
    """The maximum number of items per page requested from the API."""

    total: int
    """Total number of items matching the query, as reported by the first page."""

    desc: bool
    """Whether the items are sorted in descending order."""

    def __init__(self, first_page: Any, iterator: Iterator[T]) -> None:
        """Initialize a page wrapper from a Pydantic paginated model and an iterator over all items."""
        self.items = first_page.items
        self.count = getattr(first_page, 'count', len(first_page.items))
        self.offset = getattr(first_page, 'offset', 0)
        self.limit = getattr(first_page, 'limit', 0)
        self.total = getattr(first_page, 'total', len(first_page.items))
        self.desc = getattr(first_page, 'desc', False)
        self._first_page = first_page
        self._iterator = iterator

    def __iter__(self) -> Iterator[T]:
        """Return an iterator over all items across pages, fetching additional pages as needed."""
        return self._iterator


@docs_group('Other')
class IterableListPageAsync(AsyncIterable[T], Generic[T]):
    """An awaitable result that can also be asynchronously iterated to yield items across pages.

    Awaiting the instance (`await client.list(...)`) performs a single API call and returns a
    populated `IterableListPage`. Iterating (`async for item in client.list(...)`) yields individual
    items and performs additional API calls as needed to fetch further pages.

    A single instance supports either awaiting or iterating — not both.
    """

    def __init__(
        self,
        make_awaitable: Callable[[], Awaitable[IterableListPage[T]]],
        async_iterator: AsyncIterator[T],
    ) -> None:
        """Initialize with a factory that creates the awaitable on demand and the async iterator over items."""
        self._make_awaitable = make_awaitable
        self._async_iterator = async_iterator

    def __aiter__(self) -> AsyncIterator[T]:
        """Return an asynchronous iterator over all items across pages."""
        return self._async_iterator

    def __await__(self) -> Generator[Any, Any, IterableListPage[T]]:
        """Return an awaitable that resolves to an `IterableListPage` containing the first page."""
        return self._make_awaitable().__await__()


def build_iterable_list_page(
    callback: Callable[..., Any],
    **kwargs: Any,
) -> IterableListPage[Any]:
    """Build an `IterableListPage` from a paginated sync callback.

    The callback is invoked once immediately to fetch the first page, and again lazily during
    iteration to fetch further pages. The `total` field from the first page is not trusted for
    stopping iteration because it may change between calls; iteration stops when a page has
    no items or when the user-requested `limit` has been reached.

    Recognized kwargs:
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

    def iterator() -> Iterator[Any]:
        current_page = first_page
        yield from current_page.items

        fetched_items = len(current_page.items)
        while current_page.items and (not limit or (limit > fetched_items)):
            new_kwargs = {
                **kwargs,
                'offset': offset + fetched_items,
                'limit': chunk_size if not limit else _min_for_limit_param(limit - fetched_items, chunk_size),
            }
            current_page = callback(**new_kwargs)
            yield from current_page.items
            fetched_items += len(current_page.items)

    return IterableListPage(first_page, iterator())


def build_iterable_list_page_async(
    callback: Callable[..., Awaitable[Any]],
    **kwargs: Any,
) -> IterableListPageAsync[Any]:
    """Build an `IterableListPageAsync` from a paginated async callback.

    Mirrors `build_iterable_list_page` but for async callbacks. The returned object is both
    awaitable (resolves to the first page wrapped in `IterableListPage`) and asynchronously
    iterable (yields items across pages).
    """
    chunk_size = kwargs.pop('chunk_size', 0) or 0
    offset = kwargs.get('offset') or 0
    limit = kwargs.get('limit') or 0

    async def fetch_first_page() -> Any:
        return await callback(**{**kwargs, 'limit': _min_for_limit_param(kwargs.get('limit'), chunk_size)})

    async def async_iterator() -> AsyncIterator[Any]:
        current_page = await fetch_first_page()
        for item in current_page.items:
            yield item

        fetched_items = len(current_page.items)
        while current_page.items and (not limit or (limit > fetched_items)):
            new_kwargs = {
                **kwargs,
                'offset': offset + fetched_items,
                'limit': chunk_size if not limit else _min_for_limit_param(limit - fetched_items, chunk_size),
            }
            current_page = await callback(**new_kwargs)
            for item in current_page.items:
                yield item
            fetched_items += len(current_page.items)

    async def wrap_first_page() -> IterableListPage[Any]:
        first_page = await fetch_first_page()
        return IterableListPage(first_page, iter(first_page.items))

    return IterableListPageAsync(wrap_first_page, async_iterator())
