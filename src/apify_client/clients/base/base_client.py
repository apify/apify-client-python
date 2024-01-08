from __future__ import annotations

from typing import TYPE_CHECKING, Any

from apify_shared.utils import ignore_docs

from apify_client._logging import WithLogDetailsClient
from apify_client._utils import to_safe_id

# Conditional import only executed when type checking, otherwise we'd get circular dependency issues
if TYPE_CHECKING:
    from apify_client import ApifyClient, ApifyClientAsync
    from apify_client._http_client import HTTPClient, HTTPClientAsync


class _BaseBaseClient(metaclass=WithLogDetailsClient):
    resource_id: str | None
    url: str
    params: dict
    http_client: HTTPClient | HTTPClientAsync
    root_client: ApifyClient | ApifyClientAsync

    def _url(self: _BaseBaseClient, path: str | None = None) -> str:
        if path is not None:
            return f'{self.url}/{path}'
        return self.url

    def _params(self: _BaseBaseClient, **kwargs: Any) -> dict:
        return {
            **self.params,
            **kwargs,
        }

    def _sub_resource_init_options(self: _BaseBaseClient, **kwargs: Any) -> dict:
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


@ignore_docs
class BaseClient(_BaseBaseClient):
    """Base class for sub-clients."""

    http_client: HTTPClient
    root_client: ApifyClient

    @ignore_docs
    def __init__(
        self: BaseClient,
        *,
        base_url: str,
        root_client: ApifyClient,
        http_client: HTTPClient,
        resource_id: str | None = None,
        resource_path: str,
        params: dict | None = None,
    ) -> None:
        """Initialize the sub-client.

        Args:
            base_url (str): Base URL of the API server
            root_client (ApifyClient): The ApifyClient instance under which this resource client exists
            http_client (HTTPClient): The HTTPClient instance to be used in this client
            resource_id (str): ID of the manipulated resource, in case of a single-resource client
            resource_path (str): Path to the resource's endpoint on the API server
            params (dict): Parameters to include in all requests from this client
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


@ignore_docs
class BaseClientAsync(_BaseBaseClient):
    """Base class for async sub-clients."""

    http_client: HTTPClientAsync
    root_client: ApifyClientAsync

    @ignore_docs
    def __init__(
        self: BaseClientAsync,
        *,
        base_url: str,
        root_client: ApifyClientAsync,
        http_client: HTTPClientAsync,
        resource_id: str | None = None,
        resource_path: str,
        params: dict | None = None,
    ) -> None:
        """Initialize the sub-client.

        Args:
            base_url (str): Base URL of the API server
            root_client (ApifyClientAsync): The ApifyClientAsync instance under which this resource client exists
            http_client (HTTPClientAsync): The HTTPClientAsync instance to be used in this client
            resource_id (str): ID of the manipulated resource, in case of a single-resource client
            resource_path (str): Path to the resource's endpoint on the API server
            params (dict): Parameters to include in all requests from this client
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
