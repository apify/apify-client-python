from __future__ import annotations

from collections.abc import AsyncIterable, AsyncIterator, Awaitable, Callable, Generator, Iterable, Iterator
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    Protocol,
    TypeVar,
)

from apify_client._logging import WithLogDetailsClient
from apify_client._types import ListPage
from apify_client._utils import to_safe_id

# Conditional import only executed when type checking, otherwise we'd get circular dependency issues
if TYPE_CHECKING:
    from apify_client import ApifyClient, ApifyClientAsync
    from apify_client._http_client import HTTPClient, HTTPClientAsync
T = TypeVar('T')


class _BaseBaseClient(metaclass=WithLogDetailsClient):
    resource_id: str | None
    url: str
    params: dict
    http_client: HTTPClient | HTTPClientAsync
    root_client: ApifyClient | ApifyClientAsync

    def _url(self, path: str | None = None, *, public: bool = False) -> str:
        url = f'{self.url}/{path}' if path is not None else self.url

        if public:
            if not url.startswith(self.root_client.base_url):
                raise ValueError('API based URL has to start with `self.root_client.base_url`')
            return url.replace(self.root_client.base_url, self.root_client.public_base_url, 1)
        return url

    def _params(self, **kwargs: Any) -> dict:
        return {
            **self.params,
            **kwargs,
        }

    def _sub_resource_init_options(self, **kwargs: Any) -> dict:
        options = {
            'base_url': self.url,
            'http_client': self.http_client,
            'params': self.params,
            'root_client': self.root_client,
        }

        return {
            **options,
            **kwargs,
        }


class BaseClient(_BaseBaseClient):
    """Base class for sub-clients."""

    http_client: HTTPClient
    root_client: ApifyClient

    def __init__(
        self,
        *,
        base_url: str,
        root_client: ApifyClient,
        http_client: HTTPClient,
        resource_id: str | None = None,
        resource_path: str,
        params: dict | None = None,
    ) -> None:
        """Initialize a new instance.

        Args:
            base_url: Base URL of the API server.
            root_client: The ApifyClient instance under which this resource client exists.
            http_client: The HTTPClient instance to be used in this client.
            resource_id: ID of the manipulated resource, in case of a single-resource client.
            resource_path: Path to the resource's endpoint on the API server.
            params: Parameters to include in all requests from this client.
        """
        if resource_path.endswith('/'):
            raise ValueError('resource_path must not end with "/"')

        self.base_url = base_url
        self.root_client = root_client
        self.http_client = http_client
        self.params = params or {}
        self.resource_path = resource_path
        self.resource_id = resource_id
        self.url = f'{self.base_url}/{self.resource_path}'
        if self.resource_id is not None:
            self.safe_id = to_safe_id(self.resource_id)
            self.url = f'{self.url}/{self.safe_id}'

    @staticmethod
    def _list_iterable_from_callback(callback: Callable[..., ListPage[T]], **kwargs: Any) -> ListPageProtocol[T]:
        """Return object can be awaited or iterated over.

        Not using total from the API response as it can change during iteration.
        """
        chunk_size = kwargs.pop('chunk_size', 0) or 0
        offset = kwargs.get('offset') or 0
        limit = kwargs.get('limit') or 0

        list_page = callback(**{**kwargs, 'limit': _min_for_limit_param(kwargs.get('limit'), chunk_size)})

        def iterator() -> Iterator[T]:
            current_page = list_page
            for item in current_page.items:
                yield item

            fetched_items = len(current_page.items)
            while (
                current_page.items  # If there are any items left to fetch
                and (not limit or (limit > fetched_items))  # If there is limit to fetch, and it was not reached it yet.
            ):
                new_kwargs = {
                    **kwargs,
                    'offset': offset + fetched_items,
                    'limit': chunk_size if not limit else _min_for_limit_param(limit - fetched_items, chunk_size),
                }
                current_page = callback(**new_kwargs)
                for item in current_page.items:
                    yield item
                fetched_items += len(current_page.items)

        return IterableListPage[T](list_page, iterator())


class BaseClientAsync(_BaseBaseClient):
    """Base class for async sub-clients."""

    http_client: HTTPClientAsync
    root_client: ApifyClientAsync

    def __init__(
        self,
        *,
        base_url: str,
        root_client: ApifyClientAsync,
        http_client: HTTPClientAsync,
        resource_id: str | None = None,
        resource_path: str,
        params: dict | None = None,
    ) -> None:
        """Initialize a new instance.

        Args:
            base_url: Base URL of the API server.
            root_client: The ApifyClientAsync instance under which this resource client exists.
            http_client: The HTTPClientAsync instance to be used in this client.
            resource_id: ID of the manipulated resource, in case of a single-resource client.
            resource_path: Path to the resource's endpoint on the API server.
            params: Parameters to include in all requests from this client.
        """
        if resource_path.endswith('/'):
            raise ValueError('resource_path must not end with "/"')

        self.base_url = base_url
        self.root_client = root_client
        self.http_client = http_client
        self.params = params or {}
        self.resource_path = resource_path
        self.resource_id = resource_id
        self.url = f'{self.base_url}/{self.resource_path}'
        if self.resource_id is not None:
            self.safe_id = to_safe_id(self.resource_id)
            self.url = f'{self.url}/{self.safe_id}'

    @staticmethod
    def _list_iterable_from_callback(
        callback: Callable[..., Awaitable[ListPage[T]]], **kwargs: Any
    ) -> ListPageProtocolAsync[T]:
        """Return object can be awaited or iterated over.

        Not using total from the API response as it can change during iteration.
        """
        chunk_size = kwargs.pop('chunk_size', 0) or 0
        offset = kwargs.get('offset') or 0
        limit = kwargs.get('limit') or 0

        list_page_awaitable = callback(**{**kwargs, 'limit': _min_for_limit_param(kwargs.get('limit'), chunk_size)})

        async def async_iterator() -> AsyncIterator[T]:
            current_page = await list_page_awaitable
            for item in current_page.items:
                yield item

            fetched_items = len(current_page.items)
            while (
                current_page.items  # If there are any items left to fetch
                and (not limit or (limit > fetched_items))  # If there is limit to fetch, and it was not reached it yet.
            ):
                new_kwargs = {
                    **kwargs,
                    'offset': offset + fetched_items,
                    'limit': chunk_size if not limit else _min_for_limit_param(limit - fetched_items, chunk_size),
                }
                current_page = await callback(**new_kwargs)
                for item in current_page.items:
                    yield item
                fetched_items += len(current_page.items)

        return IterableListPageAsync[T](list_page_awaitable, async_iterator())


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


class ListPageProtocol(Iterable[T], Protocol[T]):
    """Protocol for an object that can be both awaited and asynchronously iterated over."""

    items: list[T]
    """List of returned objects on this page."""

    count: int
    """Count of the returned objects on this page."""

    offset: int
    """The limit on the number of returned objects offset specified in the API call."""

    limit: int
    """The offset of the first object specified in the API call"""

    total: int
    """Total number of objects matching the API call criteria."""

    desc: bool
    """Whether the listing is descending or not."""


class ListPageProtocolAsync(AsyncIterable[T], Awaitable[ListPage[T]], Protocol[T]):
    """Protocol for an object that can be both awaited and asynchronously iterated over."""


class IterableListPage(ListPage[T], Generic[T]):
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
