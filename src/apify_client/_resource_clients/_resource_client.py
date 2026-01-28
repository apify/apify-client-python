from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypedDict
from urllib.parse import urlencode

from apify_client._logging import WithLogDetailsClient
from apify_client._utils import to_safe_id

if TYPE_CHECKING:
    from apify_client._http_client import HttpClient, HttpClientAsync


class NestedClientConfig(TypedDict, total=False):
    """Configuration for initializing a nested resource client.

    This dict is passed as **kwargs to nested client constructors to propagate
    parent client context (HTTP client, parameters, URL hierarchy).
    """

    base_url: str
    public_base_url: str
    http_client: HttpClient | HttpClientAsync
    params: dict
    resource_id: str | None
    resource_path: str | None


class ResourceClient(metaclass=WithLogDetailsClient):
    """Base class for synchronous resource clients manipulating Apify resources.

    This class provides utility methods for both individual and collection resource clients.
    All methods are synchronous utilities that don't perform I/O operations.
    """

    def __init__(
        self,
        *,
        base_url: str,
        public_base_url: str,
        http_client: HttpClient,
        resource_path: str,
        resource_id: str | None = None,
        params: dict | None = None,
    ) -> None:
        """Initialize a new instance.

        Args:
            base_url: Base URL of the API server.
            public_base_url: Public base URL for CDN access.
            http_client: The HttpClient instance to be used in this client.
            resource_path: Path to the resource's endpoint on the API server.
            resource_id: ID of the manipulated resource, in case of a single-resource client.
            params: Parameters to include in all requests from this client.
        """
        if resource_path.endswith('/'):
            raise ValueError('resource_path must not end with "/"')

        self._base_url = base_url
        self._public_base_url = public_base_url
        self._http_client = http_client
        self._default_params = params or {}
        self._resource_path = resource_path
        self._resource_id = resource_id

    @property
    def _resource_url(self) -> str:
        resource_url = f'{self._base_url}/{self._resource_path}'

        if self._resource_id is not None:
            safe_id = to_safe_id(self._resource_id)
            resource_url = f'{resource_url}/{safe_id}'

        return resource_url

    def _build_url(
        self,
        path: str | None = None,
        *,
        public: bool = False,
        params: dict | None = None,
    ) -> str:
        """Build URL for API requests.

        Args:
            path: Optional path segment to append to resource URL
            public: If True, convert to public URL (e.g., api.apify.com → cdn.apify.com)
            params: Optional query parameters to append to URL

        Returns:
            Complete URL with path and optional query string

        Raises:
            ValueError: If public=True but URL doesn't start with base_url

        Examples:
            >>> self._url('items')
            'https://api.apify.com/v2/datasets/abc/items'

            >>> self._url('items', public=True, params={'format': 'json'})
            'https://cdn.apify.com/v2/datasets/abc/items?format=json'
        """
        # Build base URL
        url = f'{self._resource_url}/{path}' if path is not None else self._resource_url

        # Convert to public URL if requested
        if public:
            if not url.startswith(self._base_url):
                raise ValueError(f'Cannot convert to public URL: {url} does not start with base URL {self._base_url}')
            url = url.replace(self._base_url, self._public_base_url, 1)

        # Append query parameters if provided
        if params:
            # Filter None values
            filtered_params = {k: v for k, v in params.items() if v is not None}
            if filtered_params:
                separator = '&' if '?' in url else '?'
                url += separator + urlencode(filtered_params)

        return url

    def _build_params(self, **kwargs: Any) -> dict:
        """Build request parameters by merging instance params with method params.

        Automatically filters out None values to avoid sending unnecessary
        parameters to the API.

        Args:
            **kwargs: Method-specific parameters to merge with instance params

        Returns:
            Merged parameter dict with None values removed

        Example:
            >>> self._build_params(limit=10, offset=None)
            {'token': 'abc', 'limit': 10}  # offset filtered out
        """
        merged = {**self._default_params, **kwargs}
        return {k: v for k, v in merged.items() if v is not None}

    def _nested_client_config(self, **kwargs: Any) -> NestedClientConfig:
        """Build configuration dict for initializing a nested resource client.

        Creates a context propagation dict that allows child resource clients
        to inherit HTTP infrastructure, parameters, and URL hierarchy from
        their parent client.

        Args:
            **kwargs: Optional overrides (resource_path, resource_id, params, etc.)

        Returns:
            Configuration dict ready for unpacking into nested client constructor

        Example:
            >>> return BuildCollectionClient(**self._nested_client_config(resource_path='builds'))
        """
        options: NestedClientConfig = {
            'base_url': self._resource_url,
            'public_base_url': self._public_base_url,
            'http_client': self._http_client,
            'params': self._default_params,
        }
        return {**options, **kwargs}

    def _create_sibling_client(
        self,
        client_class: type,
        *,
        resource_id: str,
        resource_path: str | None = None,
        **kwargs: Any,
    ) -> Any:
        """Create a sibling resource client (e.g., RunClient from ActorClient).

        This is used when a resource client needs to create another resource client
        at the same level of the API hierarchy, not as a nested resource.

        Args:
            client_class: The class of the sibling client to create
            resource_id: ID of the sibling resource
            resource_path: Resource path for the sibling (if None, extracted from client class __init__)
            **kwargs: Additional parameters to pass to the sibling client

        Returns:
            Instance of the sibling client

        Example:
            >>> run_client = self._create_sibling_client(RunClient, resource_id=run_id)
        """
        config: dict[str, Any] = {
            'base_url': self._base_url,
            'public_base_url': self._public_base_url,
            'http_client': self._http_client,
            'resource_id': resource_id,
            'params': self._default_params.copy(),
            **kwargs,
        }

        if resource_path:
            config['resource_path'] = resource_path

        return client_class(**config)


class ResourceClientAsync(metaclass=WithLogDetailsClient):
    """Base class for asynchronous resource clients manipulating Apify resources.

    This class provides utility methods for both individual and collection resource clients.
    All methods are synchronous utilities that don't perform I/O operations.
    """

    def __init__(
        self,
        *,
        base_url: str,
        public_base_url: str,
        http_client: HttpClientAsync,
        resource_path: str,
        resource_id: str | None = None,
        params: dict | None = None,
    ) -> None:
        """Initialize a new instance.

        Args:
            base_url: Base URL of the API server.
            public_base_url: Public base URL for CDN access.
            http_client: The HttpClientAsync instance to be used in this client.
            resource_path: Path to the resource's endpoint on the API server.
            resource_id: ID of the manipulated resource, in case of a single-resource client.
            params: Parameters to include in all requests from this client.
        """
        if resource_path.endswith('/'):
            raise ValueError('resource_path must not end with "/"')

        self._base_url = base_url
        self._public_base_url = public_base_url
        self._http_client = http_client
        self._default_params = params or {}
        self._resource_path = resource_path
        self._resource_id = resource_id

    @property
    def _resource_url(self) -> str:
        resource_url = f'{self._base_url}/{self._resource_path}'

        if self._resource_id is not None:
            safe_id = to_safe_id(self._resource_id)
            resource_url = f'{resource_url}/{safe_id}'

        return resource_url

    def _build_url(
        self,
        path: str | None = None,
        *,
        public: bool = False,
        params: dict | None = None,
    ) -> str:
        """Build URL for API requests.

        Args:
            path: Optional path segment to append to resource URL
            public: If True, convert to public URL (e.g., api.apify.com → cdn.apify.com)
            params: Optional query parameters to append to URL

        Returns:
            Complete URL with path and optional query string

        Raises:
            ValueError: If public=True but URL doesn't start with base_url

        Examples:
            >>> self._url('items')
            'https://api.apify.com/v2/datasets/abc/items'

            >>> self._url('items', public=True, params={'format': 'json'})
            'https://cdn.apify.com/v2/datasets/abc/items?format=json'
        """
        # Build base URL
        url = f'{self._resource_url}/{path}' if path is not None else self._resource_url

        # Convert to public URL if requested
        if public:
            if not url.startswith(self._base_url):
                raise ValueError(f'Cannot convert to public URL: {url} does not start with base URL {self._base_url}')
            url = url.replace(self._base_url, self._public_base_url, 1)

        # Append query parameters if provided
        if params:
            # Filter None values
            filtered_params = {k: v for k, v in params.items() if v is not None}
            if filtered_params:
                separator = '&' if '?' in url else '?'
                url += separator + urlencode(filtered_params)

        return url

    def _build_params(self, **kwargs: Any) -> dict:
        """Build request parameters by merging instance params with method params.

        Automatically filters out None values to avoid sending unnecessary
        parameters to the API.

        Args:
            **kwargs: Method-specific parameters to merge with instance params

        Returns:
            Merged parameter dict with None values removed

        Example:
            >>> self._build_params(limit=10, offset=None)
            {'token': 'abc', 'limit': 10}  # offset filtered out
        """
        merged = {**self._default_params, **kwargs}
        return {k: v for k, v in merged.items() if v is not None}

    def _nested_client_config(self, **kwargs: Any) -> NestedClientConfig:
        """Build configuration dict for initializing a nested resource client.

        Creates a context propagation dict that allows child resource clients
        to inherit HTTP infrastructure, parameters, and URL hierarchy from
        their parent client.

        Args:
            **kwargs: Optional overrides (resource_path, resource_id, params, etc.)

        Returns:
            Configuration dict ready for unpacking into nested client constructor

        Example:
            >>> return BuildCollectionClientAsync(**self._nested_client_config(resource_path='builds'))
        """
        options: NestedClientConfig = {
            'base_url': self._resource_url,
            'public_base_url': self._public_base_url,
            'http_client': self._http_client,
            'params': self._default_params,
        }
        return {**options, **kwargs}

    def _create_sibling_client(
        self,
        client_class: type,
        *,
        resource_id: str,
        resource_path: str | None = None,
        **kwargs: Any,
    ) -> Any:
        """Create a sibling resource client (e.g., RunClientAsync from ActorClientAsync).

        This is used when a resource client needs to create another resource client
        at the same level of the API hierarchy, not as a nested resource.

        Args:
            client_class: The class of the sibling client to create
            resource_id: ID of the sibling resource
            resource_path: Resource path for the sibling (if None, extracted from client class __init__)
            **kwargs: Additional parameters to pass to the sibling client

        Returns:
            Instance of the sibling client

        Example:
            >>> run_client = self._create_sibling_client(RunClientAsync, resource_id=run_id)
        """
        config: dict[str, Any] = {
            'base_url': self._base_url,
            'public_base_url': self._public_base_url,
            'http_client': self._http_client,
            'resource_id': resource_id,
            'params': self._default_params.copy(),
            **kwargs,
        }

        if resource_path:
            config['resource_path'] = resource_path

        return client_class(**config)
