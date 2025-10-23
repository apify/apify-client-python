from __future__ import annotations

from apify_client._utils import catch_not_found_or_throw, parse_date_fields, pluck_data
from apify_client.clients.base.base_client import BaseClient, BaseClientAsync
from apify_client.errors import ApifyApiError


class ResourceClient(BaseClient):
    """Base class for sub-clients manipulating a single resource."""

    def _get(self, timeout_secs: int | None = None) -> dict | None:
        try:
            response = self.http_client.call(
                url=self.url,
                method='GET',
                params=self._params(),
                timeout_secs=timeout_secs,
            )

            return parse_date_fields(pluck_data(response.json()))

        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

        return None

    def _update(self, updated_fields: dict, timeout_secs: int | None = None) -> dict:
        response = self.http_client.call(
            url=self._url(),
            method='PUT',
            params=self._params(),
            json=updated_fields,
            timeout_secs=timeout_secs,
        )

        return parse_date_fields(pluck_data(response.json()))

    def _delete(self, timeout_secs: int | None = None) -> None:
        try:
            self.http_client.call(
                url=self._url(),
                method='DELETE',
                params=self._params(),
                timeout_secs=timeout_secs,
            )

        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)


class ResourceClientAsync(BaseClientAsync):
    """Base class for async sub-clients manipulating a single resource."""

    async def _get(self, timeout_secs: int | None = None) -> dict | None:
        try:
            response = await self.http_client.call(
                url=self.url,
                method='GET',
                params=self._params(),
                timeout_secs=timeout_secs,
            )

            return parse_date_fields(pluck_data(response.json()))

        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

        return None

    async def _update(self, updated_fields: dict, timeout_secs: int | None = None) -> dict:
        response = await self.http_client.call(
            url=self._url(),
            method='PUT',
            params=self._params(),
            json=updated_fields,
            timeout_secs=timeout_secs,
        )

        return parse_date_fields(pluck_data(response.json()))

    async def _delete(self, timeout_secs: int | None = None) -> None:
        try:
            await self.http_client.call(
                url=self._url(),
                method='DELETE',
                params=self._params(),
                timeout_secs=timeout_secs,
            )

        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)
