from __future__ import annotations

from typing import TYPE_CHECKING, Any

from apify_client._docs import docs_group
from apify_client._iterable_list import (
    AwaitableAsyncIterable,
    IterableListOfEnvVars,
    build_awaitable_async_iterable_offset,
    build_iterable_offset,
)
from apify_client._models import EnvVar, EnvVarResponse
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync

if TYPE_CHECKING:
    from apify_client._types import Timeout


@docs_group('Resource clients')
class ActorEnvVarCollectionClient(ResourceClient):
    """Sub-client for the Actor environment variable collection.

    Provides methods to manage Actor environment variables, e.g. list or create them. Obtain an instance via an
    appropriate method on the `ActorVersionClient` class.
    """

    def __init__(
        self,
        *,
        resource_path: str = 'env-vars',
        **kwargs: Any,
    ) -> None:
        super().__init__(
            resource_path=resource_path,
            **kwargs,
        )

    def list(self, *, timeout: Timeout = 'short') -> IterableListOfEnvVars:
        """List the available Actor environment variables.

        The returned page also supports iteration: `for item in client.list()` yields individual environment
        variables.

        https://docs.apify.com/api/v2#/reference/actors/environment-variable-collection/get-list-of-environment-variables

        Args:
            timeout: Timeout for the API HTTP request.

        Returns:
            The list of available Actor environment variables.
        """

        def _callback(**kwargs: Any) -> IterableListOfEnvVars:
            result = self._list(timeout=timeout, **kwargs)
            return IterableListOfEnvVars.model_validate(result.get('data') if isinstance(result, dict) else result)

        return build_iterable_offset(_callback)

    def create(
        self,
        *,
        is_secret: bool | None = None,
        name: str,
        value: str,
        timeout: Timeout = 'short',
    ) -> EnvVar:
        """Create a new Actor environment variable.

        https://docs.apify.com/api/v2#/reference/actors/environment-variable-collection/create-environment-variable

        Args:
            is_secret: Whether the environment variable is secret or not.
            name: The name of the environment variable.
            value: The value of the environment variable.
            timeout: Timeout for the API HTTP request.

        Returns:
            The created Actor environment variable.
        """
        result = self._create(
            timeout=timeout,
            **EnvVar(name=name, value=value, is_secret=is_secret).model_dump(by_alias=True, exclude_none=True),
        )
        return EnvVarResponse.model_validate(result).data


@docs_group('Resource clients')
class ActorEnvVarCollectionClientAsync(ResourceClientAsync):
    """Sub-client for the Actor environment variable collection.

    Provides methods to manage Actor environment variables, e.g. list or create them. Obtain an instance via an
    appropriate method on the `ActorVersionClientAsync` class.
    """

    def __init__(
        self,
        *,
        resource_path: str = 'env-vars',
        **kwargs: Any,
    ) -> None:
        super().__init__(
            resource_path=resource_path,
            **kwargs,
        )

    def list(self, *, timeout: Timeout = 'short') -> AwaitableAsyncIterable[IterableListOfEnvVars, EnvVar]:
        """List the available Actor environment variables.

        The returned page also supports iteration: `for item in client.list()` yields individual environment
        variables.

        https://docs.apify.com/api/v2#/reference/actors/environment-variable-collection/get-list-of-environment-variables

        Args:
            timeout: Timeout for the API HTTP request.

        Returns:
            The list of available Actor environment variables.
        """

        async def _callback(**kwargs: Any) -> IterableListOfEnvVars:
            result = await self._list(timeout=timeout, **kwargs)
            return IterableListOfEnvVars.model_validate(result.get('data') if isinstance(result, dict) else result)

        return build_awaitable_async_iterable_offset(_callback)

    async def create(
        self,
        *,
        is_secret: bool | None = None,
        name: str,
        value: str,
        timeout: Timeout = 'short',
    ) -> EnvVar:
        """Create a new Actor environment variable.

        https://docs.apify.com/api/v2#/reference/actors/environment-variable-collection/create-environment-variable

        Args:
            is_secret: Whether the environment variable is secret or not.
            name: The name of the environment variable.
            value: The value of the environment variable.
            timeout: Timeout for the API HTTP request.

        Returns:
            The created Actor environment variable.
        """
        result = await self._create(
            timeout=timeout,
            **EnvVar(name=name, value=value, is_secret=is_secret).model_dump(by_alias=True, exclude_none=True),
        )
        return EnvVarResponse.model_validate(result).data
