from __future__ import annotations

from typing import TYPE_CHECKING, Any

from apify_client._logging import WithLogDetailsClient
from apify_client._utils import response_to_dict, to_safe_id

if TYPE_CHECKING:
    from apify_client._client import ApifyClient, ApifyClientAsync
    from apify_client._http_client import HTTPClient, HTTPClientAsync


class BaseCollectionClient(metaclass=WithLogDetailsClient):
    """Base class for sub-clients manipulating a resource collection."""

    resource_id: str | None
    url: str
    params: dict
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

    def _create(self, resource: dict) -> dict:
        response = self.http_client.call(
            url=self._url(),
            method='POST',
            params=self._params(),
            json=resource,
        )

        return response_to_dict(response)

    def _get_or_create(self, name: str | None = None, resource: dict | None = None) -> dict:
        response = self.http_client.call(
            url=self._url(),
            method='POST',
            params=self._params(name=name),
            json=resource,
        )

        return response_to_dict(response)


class BaseCollectionClientAsync(metaclass=WithLogDetailsClient):
    """Base class for async sub-clients manipulating a resource collection."""

    resource_id: str | None
    url: str
    params: dict
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

    async def _create(self, resource: dict) -> dict:
        response = await self.http_client.call(
            url=self._url(),
            method='POST',
            params=self._params(),
            json=resource,
        )

        return response_to_dict(response)

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

        return response_to_dict(response)
