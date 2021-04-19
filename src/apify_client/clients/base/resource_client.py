from typing import Dict, Optional

from ..._errors import ApifyApiError
from ..._utils import _catch_not_found_or_throw, _parse_date_fields, _pluck_data
from .base_client import BaseClient


class ResourceClient(BaseClient):
    """Base class for sub-clients manipulating a single resource."""

    def _get(self) -> Optional[Dict]:
        try:
            response = self.http_client.call(
                url=self.url,
                method='GET',
                params=self._params(),
            )

            return _parse_date_fields(_pluck_data(response.json()))

        except ApifyApiError as exc:
            _catch_not_found_or_throw(exc)

        return None

    def _update(self, updated_fields: Dict) -> Dict:
        response = self.http_client.call(
            url=self._url(),
            method='PUT',
            params=self._params(),
            json=updated_fields,
        )

        return _parse_date_fields(_pluck_data(response.json()))

    def _delete(self) -> None:
        try:
            self.http_client.call(
                url=self._url(),
                method='DELETE',
                params=self._params(),
            )

        except ApifyApiError as exc:
            _catch_not_found_or_throw(exc)
