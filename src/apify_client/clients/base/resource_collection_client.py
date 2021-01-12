from typing import Any, Dict

from ..._utils import _parse_date_fields, _pluck_data
from .base_client import BaseClient


class ResourceCollectionClient(BaseClient):
    """Base class for sub-clients manipulating a resource collection."""

    def _list(self, **kwargs: Any) -> Any:
        response = self.http_client.call(
            url=self._url(),
            method='GET',
            params=self._params(**kwargs),
        )

        return _parse_date_fields(_pluck_data(response.json()))

    def _create(self, resource: Dict) -> Any:
        response = self.http_client.call(
            url=self._url(),
            method='POST',
            params=self._params(),
            json=resource,
        )

        return _parse_date_fields(_pluck_data(response.json()))

    def _get_or_create(self, name: str = '') -> Any:
        response = self.http_client.call(
            url=self._url(),
            method='POST',
            params=self._params(name=name),
        )

        return _parse_date_fields(_pluck_data(response.json()))
