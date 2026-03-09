from __future__ import annotations

from typing import TYPE_CHECKING, Any

from apify_client._docs import docs_group
from apify_client._models import EnvVar, EnvVarResponse
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync

if TYPE_CHECKING:
    from apify_client._types import Timeout


@docs_group('Resource clients')
class ActorEnvVarClient(ResourceClient):
    """Sub-client for managing a specific Actor environment variable.

    Provides methods to manage a specific Actor environment variable, e.g. get, update, or delete it. Obtain an instance
    via an appropriate method on the `ActorVersionClient` class.
    """

    def __init__(
        self,
        *,
        resource_id: str,
        resource_path: str = 'env-vars',
        **kwargs: Any,
    ) -> None:
        super().__init__(
            resource_id=resource_id,
            resource_path=resource_path,
            **kwargs,
        )

    def get(self, *, timeout: Timeout = 'long') -> EnvVar | None:
        """Return information about the Actor environment variable.

        https://docs.apify.com/api/v2#/reference/actors/environment-variable-object/get-environment-variable

        Args:
            timeout: Timeout for the API HTTP request.

        Returns:
            The retrieved Actor environment variable data.
        """
        result = self._get(timeout=timeout)
        if result is None:
            return None
        return EnvVarResponse.model_validate(result).data

    def update(
        self,
        *,
        is_secret: bool | None = None,
        name: str,
        value: str,
        timeout: Timeout = 'long',
    ) -> EnvVar:
        """Update the Actor environment variable with specified fields.

        https://docs.apify.com/api/v2#/reference/actors/environment-variable-object/update-environment-variable

        Args:
            is_secret: Whether the environment variable is secret or not.
            name: The name of the environment variable.
            value: The value of the environment variable.
            timeout: Timeout for the API HTTP request.

        Returns:
            The updated Actor environment variable.
        """
        result = self._update(
            timeout=timeout,
            **EnvVar(name=name, value=value, is_secret=is_secret).model_dump(by_alias=True, exclude_none=True),
        )
        return EnvVarResponse.model_validate(result).data

    def delete(self, *, timeout: Timeout = 'long') -> None:
        """Delete the Actor environment variable.

        https://docs.apify.com/api/v2#/reference/actors/environment-variable-object/delete-environment-variable

        Args:
            timeout: Timeout for the API HTTP request.
        """
        self._delete(timeout=timeout)


@docs_group('Resource clients')
class ActorEnvVarClientAsync(ResourceClientAsync):
    """Sub-client for managing a specific Actor environment variable.

    Provides methods to manage a specific Actor environment variable, e.g. get, update, or delete it. Obtain an instance
    via an appropriate method on the `ActorVersionClientAsync` class.
    """

    def __init__(
        self,
        *,
        resource_id: str,
        resource_path: str = 'env-vars',
        **kwargs: Any,
    ) -> None:
        super().__init__(
            resource_id=resource_id,
            resource_path=resource_path,
            **kwargs,
        )

    async def get(self, *, timeout: Timeout = 'long') -> EnvVar | None:
        """Return information about the Actor environment variable.

        https://docs.apify.com/api/v2#/reference/actors/environment-variable-object/get-environment-variable

        Args:
            timeout: Timeout for the API HTTP request.

        Returns:
            The retrieved Actor environment variable data.
        """
        result = await self._get(timeout=timeout)
        if result is None:
            return None
        return EnvVarResponse.model_validate(result).data

    async def update(
        self,
        *,
        is_secret: bool | None = None,
        name: str,
        value: str,
        timeout: Timeout = 'long',
    ) -> EnvVar:
        """Update the Actor environment variable with specified fields.

        https://docs.apify.com/api/v2#/reference/actors/environment-variable-object/update-environment-variable

        Args:
            is_secret: Whether the environment variable is secret or not.
            name: The name of the environment variable.
            value: The value of the environment variable.
            timeout: Timeout for the API HTTP request.

        Returns:
            The updated Actor environment variable.
        """
        result = await self._update(
            timeout=timeout,
            **EnvVar(name=name, value=value, is_secret=is_secret).model_dump(by_alias=True, exclude_none=True),
        )
        return EnvVarResponse.model_validate(result).data

    async def delete(self, *, timeout: Timeout = 'long') -> None:
        """Delete the Actor environment variable.

        https://docs.apify.com/api/v2#/reference/actors/environment-variable-object/delete-environment-variable

        Args:
            timeout: Timeout for the API HTTP request.
        """
        await self._delete(timeout=timeout)
