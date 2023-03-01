from typing import Any, Dict, Optional

from ..._utils import ListPage, _parse_date_fields, _pluck_data, ignore_docs
from .base_client import BaseClient, BaseClientAsync


@ignore_docs
class ResourceCollectionClient(BaseClient):
    """Base class for sub-clients manipulating a resource collection."""

    def _list(self, **kwargs: Any) -> ListPage:
        response = self.http_client.call(
            url=self._url(),
            method='GET',
            params=self._params(**kwargs),
        )

        return ListPage(_parse_date_fields(_pluck_data(response.json())))

    def _create(self, resource: Dict) -> Dict:
        response = self.http_client.call(
            url=self._url(),
            method='POST',
            params=self._params(),
            json=resource,
        )

        return _parse_date_fields(_pluck_data(response.json()))

    def _get_or_create(self, name: Optional[str] = None, resource: Optional[Dict] = None) -> Dict:
        response = self.http_client.call(
            url=self._url(),
            method='POST',
            params=self._params(name=name),
            json=resource,
        )

        return _parse_date_fields(_pluck_data(response.json()))


@ignore_docs
class ResourceCollectionClientAsync(BaseClientAsync):
    """Base class for async sub-clients manipulating a resource collection."""

    async def _list(self, **kwargs: Any) -> ListPage:
        response = await self.http_client.call(
            url=self._url(),
            method='GET',
            params=self._params(**kwargs),
        )

        return ListPage(_parse_date_fields(_pluck_data(response.json())))

    async def _create(self, resource: Dict) -> Dict:
        response = await self.http_client.call(
            url=self._url(),
            method='POST',
            params=self._params(),
            json=resource,
        )

        return _parse_date_fields(_pluck_data(response.json()))

    async def _get_or_create(self, name: Optional[str] = None, resource: Optional[Dict] = None) -> Dict:
        response = await self.http_client.call(
            url=self._url(),
            method='POST',
            params=self._params(name=name),
            json=resource,
        )

        return _parse_date_fields(_pluck_data(response.json()))
