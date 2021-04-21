from typing import Any, Dict, Optional

from ..._utils import ListPage, _parse_date_fields, _pluck_data
from .base_client import BaseClient


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

    def _get_or_create(self, name: Optional[str] = None) -> Dict:
        response = self.http_client.call(
            url=self._url(),
            method='POST',
            params=self._params(name=name),
        )

        return _parse_date_fields(_pluck_data(response.json()))
