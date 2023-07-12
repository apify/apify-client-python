from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Optional, Union

from ..._http_client import _HTTPClient, _HTTPClientAsync
from ..._logging import _WithLogDetailsClient
from ..._utils import _to_safe_id, ignore_docs

# Conditional import only executed when type checking, otherwise we'd get circular dependency issues
if TYPE_CHECKING:
    from ...client import ApifyClient, ApifyClientAsync


class _BaseBaseClient(metaclass=_WithLogDetailsClient):
    resource_id: Optional[str]
    url: str
    params: Dict
    http_client: Union[_HTTPClient, _HTTPClientAsync]
    root_client: Union[ApifyClient, ApifyClientAsync]

    def _url(self, path: Optional[str] = None) -> str:
        if path is not None:
            return f'{self.url}/{path}'
        return self.url

    def _params(self, **kwargs: Any) -> Dict:
        return {
            **self.params,
            **kwargs,
        }

    def _sub_resource_init_options(self, **kwargs: Any) -> Dict:
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

    http_client: _HTTPClient
    root_client: ApifyClient

    @ignore_docs
    def __init__(
        self,
        *,
        base_url: str,
        root_client: ApifyClient,
        http_client: _HTTPClient,
        resource_id: Optional[str] = None,
        resource_path: str,
        params: Optional[Dict] = None,
    ) -> None:
        """Initialize the sub-client.

        Args:
            base_url (str): Base URL of the API server
            root_client (ApifyClient): The ApifyClient instance under which this resource client exists
            http_client (_HTTPClient): The _HTTPClient instance to be used in this client
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
            self.safe_id = _to_safe_id(self.resource_id)
            self.url = f'{self.url}/{self.safe_id}'


@ignore_docs
class BaseClientAsync(_BaseBaseClient):
    """Base class for async sub-clients."""

    http_client: _HTTPClientAsync
    root_client: ApifyClientAsync

    @ignore_docs
    def __init__(
        self,
        *,
        base_url: str,
        root_client: ApifyClientAsync,
        http_client: _HTTPClientAsync,
        resource_id: Optional[str] = None,
        resource_path: str,
        params: Optional[Dict] = None,
    ) -> None:
        """Initialize the sub-client.

        Args:
            base_url (str): Base URL of the API server
            root_client (ApifyClientAsync): The ApifyClientAsync instance under which this resource client exists
            http_client (_HTTPClientAsync): The _HTTPClientAsync instance to be used in this client
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
            self.safe_id = _to_safe_id(self.resource_id)
            self.url = f'{self.url}/{self.safe_id}'
