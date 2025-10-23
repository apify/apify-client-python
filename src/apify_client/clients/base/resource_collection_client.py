from __future__ import annotations

from typing import Any, Generic, TypeVar

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
