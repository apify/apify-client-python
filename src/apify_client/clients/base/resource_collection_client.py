from __future__ import annotations

from typing import Any

from apify_shared.models import ListPage
from apify_shared.utils import ignore_docs, parse_date_fields

from apify_client._utils import pluck_data
from apify_client.clients.base.base_client import BaseClient, BaseClientAsync


@ignore_docs
class ResourceCollectionClient(BaseClient):
    """Base class for sub-clients manipulating a resource collection."""

    def _list(self: ResourceCollectionClient, **kwargs: Any) -> ListPage:
        response = self.http_client.call(
            url=self._url(),
            method='GET',
            params=self._params(**kwargs),
        )

        return ListPage(parse_date_fields(pluck_data(response.json())))

    def _create(self: ResourceCollectionClient, resource: dict) -> dict:
        response = self.http_client.call(
            url=self._url(),
            method='POST',
            params=self._params(),
            json=resource,
        )

        return parse_date_fields(pluck_data(response.json()))

    def _get_or_create(
        self: ResourceCollectionClient,
        name: str | None = None,
        resource: dict | None = None,
    ) -> dict:
        response = self.http_client.call(
            url=self._url(),
            method='POST',
            params=self._params(name=name),
            json=resource,
        )

        return parse_date_fields(pluck_data(response.json()))


@ignore_docs
class ResourceCollectionClientAsync(BaseClientAsync):
    """Base class for async sub-clients manipulating a resource collection."""

    async def _list(self: ResourceCollectionClientAsync, **kwargs: Any) -> ListPage:
        response = await self.http_client.call(
            url=self._url(),
            method='GET',
            params=self._params(**kwargs),
        )

        return ListPage(parse_date_fields(pluck_data(response.json())))

    async def _create(self: ResourceCollectionClientAsync, resource: dict) -> dict:
        response = await self.http_client.call(
            url=self._url(),
            method='POST',
            params=self._params(),
            json=resource,
        )

        return parse_date_fields(pluck_data(response.json()))

    async def _get_or_create(
        self: ResourceCollectionClientAsync,
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
