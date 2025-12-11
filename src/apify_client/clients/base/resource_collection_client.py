from __future__ import annotations

from collections.abc import AsyncIterable, AsyncIterator, Awaitable, Generator, Iterable, Iterator
from typing import Any, Generic, Protocol, TypeVar

from apify_client._utils import parse_date_fields, pluck_data
from apify_client.clients.base.base_client import BaseClient, BaseClientAsync

T = TypeVar('T')


class ListPage(Generic[T]):
    """A single page of items returned from a list() method."""

    items: list[T]
    """List of returned objects on this page"""

    count: int
    """Count of the returned objects on this page"""

    offset: int
    """The limit on the number of returned objects offset specified in the API call"""

    limit: int
    """The offset of the first object specified in the API call"""

    total: int
    """Total number of objects matching the API call criteria"""

    desc: bool
    """Whether the listing is descending or not"""

    def __init__(self, data: dict) -> None:
        """Initialize a ListPage instance from the API response data."""
        self.items = data.get('items', [])
        self.offset = data.get('offset', 0)
        self.limit = data.get('limit', 0)
        self.count = data['count'] if 'count' in data else len(self.items)
        self.total = data['total'] if 'total' in data else self.offset + self.count
        self.desc = data.get('desc', False)


class ResourceCollectionClient(BaseClient):
    """Base class for sub-clients manipulating a resource collection."""

    def _list(self, **kwargs: Any) -> ListPage:
        response = self.http_client.call(
            url=self._url(),
            method='GET',
            params=self._params(**kwargs),
        )

        return ListPage(parse_date_fields(pluck_data(response.json())))


    def _list_iterable(self, **kwargs: Any) -> IterableListPage[T]:
        """Return object can be awaited or iterated over."""
        chunk_size = kwargs.pop('chunk_size', None)

        list_page = self._list(**{**kwargs, 'limit': _min_for_limit_param(kwargs.get('limit'), chunk_size)})

        def iterator() -> Iterator[T]:
            current_page = list_page
            for item in current_page.items:
                yield item

            offset = kwargs.get('offset') or 0
            limit = min(kwargs.get('limit') or current_page.total, current_page.total)

            current_offset = offset + len(current_page.items)
            remaining_items = min(current_page.total - offset, limit) - len(current_page.items)
            while current_page.items and remaining_items > 0:
                new_kwargs = {
                    **kwargs,
                    'offset': current_offset,
                    'limit': _min_for_limit_param(remaining_items, chunk_size),
                }
                current_page = self._list(**new_kwargs)
                for item in current_page.items:
                    yield item
                current_offset += len(current_page.items)
                remaining_items -= len(current_page.items)

        return IterableListPage[T](list_page, iterator())

    def _create(self, resource: dict) -> dict:
        response = self.http_client.call(
            url=self._url(),
            method='POST',
            params=self._params(),
            json=resource,
        )

        return parse_date_fields(pluck_data(response.json()))

    def _get_or_create(self, name: str | None = None, resource: dict | None = None) -> dict:
        response = self.http_client.call(
            url=self._url(),
            method='POST',
            params=self._params(name=name),
            json=resource,
        )

        return parse_date_fields(pluck_data(response.json()))


class ResourceCollectionClientAsync(BaseClientAsync):
    """Base class for async sub-clients manipulating a resource collection."""

    async def _list(self, **kwargs: Any) -> ListPage:
        response = await self.http_client.call(
            url=self._url(),
            method='GET',
            params=self._params(**kwargs),
        )

        return ListPage(parse_date_fields(pluck_data(response.json())))

    def _list_iterable(self, **kwargs: Any) -> ListPageProtocolAsync[T]:
        """Return object can be awaited or iterated over."""
        chunk_size = kwargs.pop('chunk_size', None)

        list_page_awaitable = self._list(**{**kwargs, 'limit': _min_for_limit_param(kwargs.get('limit'), chunk_size)})

        async def async_iterator() -> AsyncIterator[T]:
            current_page = await list_page_awaitable
            for item in current_page.items:
                yield item

            offset = kwargs.get('offset') or 0
            limit = min(kwargs.get('limit') or current_page.total, current_page.total)

            current_offset = offset + len(current_page.items)
            remaining_items = min(current_page.total - offset, limit) - len(current_page.items)
            while current_page.items and remaining_items > 0:
                new_kwargs = {
                    **kwargs,
                    'offset': current_offset,
                    'limit': _min_for_limit_param(remaining_items, chunk_size),
                }
                current_page = await self._list(**new_kwargs)
                for item in current_page.items:
                    yield item
                current_offset += len(current_page.items)
                remaining_items -= len(current_page.items)

        return IterableListPageAsync[T](list_page_awaitable, async_iterator())

    async def _create(self, resource: dict) -> dict:
        response = await self.http_client.call(
            url=self._url(),
            method='POST',
            params=self._params(),
            json=resource,
        )

        return parse_date_fields(pluck_data(response.json()))

    async def _get_or_create(
        self,
        name: str | None = None,
        resource: dict | None = None,
    ) -> dict:
        response = await self.http_client.call(
            url=self._url(),
            method='POST',
            params=self._params(name=name),
            json=resource,
        )

        return parse_date_fields(pluck_data(response.json()))


class ListPageProtocol(Protocol[T], Iterable[T]):
    """Protocol for an object that can be both awaited and asynchronously iterated over."""

    items: list[T]
    """List of returned objects on this page"""

    count: int
    """Count of the returned objects on this page"""

    offset: int
    """The limit on the number of returned objects offset specified in the API call"""

    limit: int
    """The offset of the first object specified in the API call"""

    total: int
    """Total number of objects matching the API call criteria"""

    desc: bool
    """Whether the listing is descending or not"""

class IterableListPage(Generic[T], ListPage[T]):
    """Can be called to get ListPage with items or iterated over to get individual items."""

    def __init__(self, list_page: ListPage[T], iterator: Iterator[T]) -> None:
        self.items = list_page.items
        self.offset = list_page.offset
        self.limit = list_page.limit
        self.count = list_page.count
        self.total = list_page.total
        self.desc = list_page.desc
        self._iterator = iterator

    def __iter__(self) -> Iterator[T]:
        """Return an iterator over the items from API, possibly doing multiple API calls."""
        return self._iterator

class ListPageProtocolAsync(Protocol[T], AsyncIterable[T], Awaitable[ListPage[T]]):
    """Protocol for an object that can be both awaited and asynchronously iterated over."""

class IterableListPageAsync(Generic[T]):
    """Can be awaited to get ListPage with items or asynchronously iterated over to get individual items."""

    def __init__(self, awaitable: Awaitable[ListPage[T]], async_iterator: AsyncIterator[T]) -> None:
        self._awaitable = awaitable
        self._async_iterator = async_iterator

    def __aiter__(self) -> AsyncIterator[T]:
        """Return an asynchronous iterator over the items from API, possibly doing multiple API calls."""
        return self._async_iterator

    def __await__(self) -> Generator[Any, Any, ListPage[T]]:
        """Return an awaitable that resolves to the ListPage doing exactly one API call."""
        return self._awaitable.__await__()


def _min_for_limit_param(a: int | None, b: int | None) -> int | None:
    """Return minimum of two limit parameters, treating None or 0 as infinity. Return None for infinity."""
    # API treats 0 as None for limit parameter, in this context API understands 0 as infinity.
    if a == 0:
        a = None
    if b == 0:
        b = None
    if a is None:
        return b
    if b is None:
        return a
    return min(a, b)
