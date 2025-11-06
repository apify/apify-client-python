"""HTTP client for Apify API with Pydantic v2 models."""

from typing import Any, Optional, TypeVar, Type
import httpx
from pydantic import BaseModel, ValidationError

T = TypeVar('T', bound=BaseModel)


class ApifyClient:
    """Synchronous Apify API client with Pydantic v2 validation."""

    def __init__(
        self,
        token: Optional[str] = None,
        base_url: str = 'https://api.apify.com/v2',
        timeout: float = 60.0,
    ):
        """Initialize the Apify client.

        Args:
            token: Apify API token for authentication
            base_url: Base URL for the Apify API
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=timeout,
            headers=self._build_headers(token),
        )

    def _build_headers(self, token: Optional[str]) -> dict[str, str]:
        """Build HTTP headers including authorization."""
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'apify-client-python-v3/3.0.0',
        }
        if token:
            headers['Authorization'] = f'Bearer {token}'
        return headers

    def get(
        self,
        path: str,
        params: Optional[dict[str, Any]] = None,
        response_model: Optional[Type[T]] = None,
    ) -> T | dict[str, Any]:
        """Make a GET request.

        Args:
            path: API endpoint path (e.g., '/acts')
            params: Query parameters
            response_model: Pydantic model to validate response

        Returns:
            Validated Pydantic model instance or raw dict

        Raises:
            httpx.HTTPStatusError: For HTTP errors
            ValidationError: For response validation errors
        """
        response = self._client.get(path, params=params)
        response.raise_for_status()

        data = response.json()
        if response_model:
            return response_model.model_validate(data)
        return data

    def post(
        self,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        response_model: Optional[Type[T]] = None,
    ) -> T | dict[str, Any]:
        """Make a POST request.

        Args:
            path: API endpoint path
            json: JSON request body
            params: Query parameters
            response_model: Pydantic model to validate response

        Returns:
            Validated Pydantic model instance or raw dict

        Raises:
            httpx.HTTPStatusError: For HTTP errors
            ValidationError: For response validation errors
        """
        response = self._client.post(path, json=json, params=params)
        response.raise_for_status()

        data = response.json()
        if response_model:
            return response_model.model_validate(data)
        return data

    def put(
        self,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        response_model: Optional[Type[T]] = None,
    ) -> T | dict[str, Any]:
        """Make a PUT request.

        Args:
            path: API endpoint path
            json: JSON request body
            params: Query parameters
            response_model: Pydantic model to validate response

        Returns:
            Validated Pydantic model instance or raw dict
        """
        response = self._client.put(path, json=json, params=params)
        response.raise_for_status()

        data = response.json()
        if response_model:
            return response_model.model_validate(data)
        return data

    def delete(
        self,
        path: str,
        params: Optional[dict[str, Any]] = None,
    ) -> None:
        """Make a DELETE request.

        Args:
            path: API endpoint path
            params: Query parameters

        Raises:
            httpx.HTTPStatusError: For HTTP errors
        """
        response = self._client.delete(path, params=params)
        response.raise_for_status()

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    def __enter__(self) -> 'ApifyClient':
        """Context manager entry."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        self.close()


class ApifyClientAsync:
    """Asynchronous Apify API client with Pydantic v2 validation."""

    def __init__(
        self,
        token: Optional[str] = None,
        base_url: str = 'https://api.apify.com/v2',
        timeout: float = 60.0,
    ):
        """Initialize the async Apify client.

        Args:
            token: Apify API token for authentication
            base_url: Base URL for the Apify API
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            headers=self._build_headers(token),
        )

    def _build_headers(self, token: Optional[str]) -> dict[str, str]:
        """Build HTTP headers including authorization."""
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'apify-client-python-v3/3.0.0',
        }
        if token:
            headers['Authorization'] = f'Bearer {token}'
        return headers

    async def get(
        self,
        path: str,
        params: Optional[dict[str, Any]] = None,
        response_model: Optional[Type[T]] = None,
    ) -> T | dict[str, Any]:
        """Make an async GET request.

        Args:
            path: API endpoint path (e.g., '/acts')
            params: Query parameters
            response_model: Pydantic model to validate response

        Returns:
            Validated Pydantic model instance or raw dict

        Raises:
            httpx.HTTPStatusError: For HTTP errors
            ValidationError: For response validation errors
        """
        response = await self._client.get(path, params=params)
        response.raise_for_status()

        data = response.json()
        if response_model:
            return response_model.model_validate(data)
        return data

    async def post(
        self,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        response_model: Optional[Type[T]] = None,
    ) -> T | dict[str, Any]:
        """Make an async POST request.

        Args:
            path: API endpoint path
            json: JSON request body
            params: Query parameters
            response_model: Pydantic model to validate response

        Returns:
            Validated Pydantic model instance or raw dict

        Raises:
            httpx.HTTPStatusError: For HTTP errors
            ValidationError: For response validation errors
        """
        response = await self._client.post(path, json=json, params=params)
        response.raise_for_status()

        data = response.json()
        if response_model:
            return response_model.model_validate(data)
        return data

    async def put(
        self,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        response_model: Optional[Type[T]] = None,
    ) -> T | dict[str, Any]:
        """Make an async PUT request.

        Args:
            path: API endpoint path
            json: JSON request body
            params: Query parameters
            response_model: Pydantic model to validate response

        Returns:
            Validated Pydantic model instance or raw dict
        """
        response = await self._client.put(path, json=json, params=params)
        response.raise_for_status()

        data = response.json()
        if response_model:
            return response_model.model_validate(data)
        return data

    async def delete(
        self,
        path: str,
        params: Optional[dict[str, Any]] = None,
    ) -> None:
        """Make an async DELETE request.

        Args:
            path: API endpoint path
            params: Query parameters

        Raises:
            httpx.HTTPStatusError: For HTTP errors
        """
        response = await self._client.delete(path, params=params)
        response.raise_for_status()

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    async def __aenter__(self) -> 'ApifyClientAsync':
        """Async context manager entry."""
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Async context manager exit."""
        await self.close()
