from __future__ import annotations

from typing import TYPE_CHECKING, Any
from urllib.parse import urlencode

from apify_client._logging import WithLogDetailsClient
from apify_client._utils import to_safe_id

if TYPE_CHECKING:
    from apify_client._client_classes import ClientRegistry, ClientRegistryAsync
    from apify_client._http_client import HttpClient, HttpClientAsync


class ResourceClient(metaclass=WithLogDetailsClient):
    """Base class for synchronous resource clients.

    Provides URL building, parameter handling, and client creation utilities.
    All methods are synchronous and don't perform I/O operations.
    """

    def __init__(
        self,
        *,
        base_url: str,
        public_base_url: str,
        http_client: HttpClient,
        resource_path: str,
        client_classes: ClientRegistry,
        resource_id: str | None = None,
        params: dict | None = None,
    ) -> None:
        """Initialize the resource client.

        Args:
            base_url: API base URL.
            public_base_url: Public CDN base URL.
            http_client: HTTP client for making requests.
            resource_path: Resource endpoint path (e.g., 'actors', 'datasets').
            client_classes: Bundle of client classes for dependency injection.
            resource_id: Optional resource ID for single-resource clients.
            params: Optional default parameters for all requests.
        """
        if resource_path.endswith('/'):
            raise ValueError('resource_path must not end with "/"')

        self._base_url = base_url
        self._public_base_url = public_base_url
        self._http_client = http_client
        self._default_params = params or {}
        self._resource_path = resource_path
        self._resource_id = resource_id
        self._client_classes = client_classes

    @property
    def _resource_url(self) -> str:
        """Build the full resource URL from base URL, path, and optional ID."""
        url = f'{self._base_url}/{self._resource_path}'
        if self._resource_id is not None:
            url = f'{url}/{to_safe_id(self._resource_id)}'
        return url

    @property
    def _base_client_kwargs(self) -> dict[str, Any]:
        """Base kwargs for creating nested/child clients.

        Returns dict with base_url, public_base_url, http_client, and client_classes. Caller adds
        resource_path, resource_id, and params as needed.
        """
        return {
            'base_url': self._resource_url,
            'public_base_url': self._public_base_url,
            'http_client': self._http_client,
            'client_classes': self._client_classes,
        }

    def _build_url(
        self,
        path: str | None = None,
        *,
        public: bool = False,
        params: dict | None = None,
    ) -> str:
        """Build complete URL for API request.

        Args:
            path: Optional path segment to append (e.g., 'runs', 'items').
            public: Whether to use public CDN URL instead of API URL.
            params: Optional query parameters to append.

        Returns:
            Complete URL with optional path and query string.
        """
        url = f'{self._resource_url}/{path}' if path else self._resource_url

        if public:
            if not url.startswith(self._base_url):
                raise ValueError(f'URL {url} does not start with base URL {self._base_url}')
            url = url.replace(self._base_url, self._public_base_url, 1)

        if params:
            filtered = {k: v for k, v in params.items() if v is not None}
            if filtered:
                separator = '&' if '?' in url else '?'
                url += separator + urlencode(filtered)

        return url

    def _build_params(self, **kwargs: Any) -> dict:
        """Merge default params with method params, filtering out None values.

        Args:
            **kwargs: Method-specific parameters to merge.

        Returns:
            Merged parameters with None values removed.
        """
        merged = {**self._default_params, **kwargs}
        return {k: v for k, v in merged.items() if v is not None}


class ResourceClientAsync(metaclass=WithLogDetailsClient):
    """Base class for asynchronous resource clients.

    Provides URL building, parameter handling, and client creation utilities.
    All methods are synchronous and don't perform I/O operations.
    """

    def __init__(
        self,
        *,
        base_url: str,
        public_base_url: str,
        http_client: HttpClientAsync,
        resource_path: str,
        client_classes: ClientRegistryAsync,
        resource_id: str | None = None,
        params: dict | None = None,
    ) -> None:
        """Initialize the resource client.

        Args:
            base_url: API base URL.
            public_base_url: Public CDN base URL.
            http_client: HTTP client for making requests.
            resource_path: Resource endpoint path (e.g., 'actors', 'datasets').
            client_classes: Bundle of client classes for dependency injection.
            resource_id: Optional resource ID for single-resource clients.
            params: Optional default parameters for all requests.
        """
        if resource_path.endswith('/'):
            raise ValueError('resource_path must not end with "/"')

        self._base_url = base_url
        self._public_base_url = public_base_url
        self._http_client = http_client
        self._default_params = params or {}
        self._resource_path = resource_path
        self._resource_id = resource_id
        self._client_classes = client_classes

    @property
    def _resource_url(self) -> str:
        """Build the full resource URL from base URL, path, and optional ID."""
        url = f'{self._base_url}/{self._resource_path}'
        if self._resource_id is not None:
            url = f'{url}/{to_safe_id(self._resource_id)}'
        return url

    @property
    def _base_client_kwargs(self) -> dict[str, Any]:
        """Base kwargs for creating nested/child clients.

        Returns dict with base_url, public_base_url, http_client, and client_classes. Caller adds
        resource_path, resource_id, and params as needed.
        """
        return {
            'base_url': self._resource_url,
            'public_base_url': self._public_base_url,
            'http_client': self._http_client,
            'client_classes': self._client_classes,
        }

    def _build_url(
        self,
        path: str | None = None,
        *,
        public: bool = False,
        params: dict | None = None,
    ) -> str:
        """Build complete URL for API request.

        Args:
            path: Optional path segment to append (e.g., 'runs', 'items').
            public: Whether to use public CDN URL instead of API URL.
            params: Optional query parameters to append.

        Returns:
            Complete URL with optional path and query string.
        """
        url = f'{self._resource_url}/{path}' if path else self._resource_url

        if public:
            if not url.startswith(self._base_url):
                raise ValueError(f'URL {url} does not start with base URL {self._base_url}')
            url = url.replace(self._base_url, self._public_base_url, 1)

        if params:
            filtered = {k: v for k, v in params.items() if v is not None}
            if filtered:
                separator = '&' if '?' in url else '?'
                url += separator + urlencode(filtered)

        return url

    def _build_params(self, **kwargs: Any) -> dict:
        """Merge default params with method params, filtering out None values.

        Args:
            **kwargs: Method-specific parameters to merge.

        Returns:
            Merged parameters with None values removed.
        """
        merged = {**self._default_params, **kwargs}
        return {k: v for k, v in merged.items() if v is not None}
