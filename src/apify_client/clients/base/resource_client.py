from __future__ import annotations

from apify_shared.utils import ignore_docs, parse_date_fields

from apify_client._errors import ApifyApiError
from apify_client._utils import catch_not_found_or_throw, pluck_data
from apify_client.clients.base.base_client import BaseClient, BaseClientAsync


@ignore_docs
class ResourceClient(BaseClient):
    """Base class for sub-clients manipulating a single resource."""

    def _get(self: ResourceClient) -> dict | None:
        try:
            response = self.http_client.call(
                url=self.url,
                method='GET',
                params=self._params(),
            )

            return parse_date_fields(pluck_data(response.json()))

        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

        return None

    def _update(self: ResourceClient, updated_fields: dict) -> dict:
        response = self.http_client.call(
            url=self._url(),
            method='PUT',
            params=self._params(),
            json=updated_fields,
        )

        return parse_date_fields(pluck_data(response.json()))

    def _delete(self: ResourceClient) -> None:
        try:
            self.http_client.call(
                url=self._url(),
                method='DELETE',
                params=self._params(),
            )

        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)


@ignore_docs
class ResourceClientAsync(BaseClientAsync):
    """Base class for async sub-clients manipulating a single resource."""

    async def _get(self: ResourceClientAsync) -> dict | None:
        try:
            response = await self.http_client.call(
                url=self.url,
                method='GET',
                params=self._params(),
            )

            return parse_date_fields(pluck_data(response.json()))

        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

        return None

    async def _update(self: ResourceClientAsync, updated_fields: dict) -> dict:
        response = await self.http_client.call(
            url=self._url(),
            method='PUT',
            params=self._params(),
            json=updated_fields,
        )

        return parse_date_fields(pluck_data(response.json()))

    async def _delete(self: ResourceClientAsync) -> None:
        try:
            await self.http_client.call(
                url=self._url(),
                method='DELETE',
                params=self._params(),
            )

        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)
