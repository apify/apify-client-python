from __future__ import annotations

from typing import Any

from apify_client._docs import docs_group
from apify_client._models import EnvVar, EnvVarResponse, ListOfEnvVars, ListOfEnvVarsResponse
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync
from apify_client._resource_clients.actor_env_var import get_actor_env_var_representation
from apify_client._utils import filter_none_values


@docs_group('Resource clients')
class ActorEnvVarCollectionClient(ResourceClient):
    """Sub-client for manipulating Actor env vars."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'env-vars')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def list(self) -> ListOfEnvVars:
        """List the available Actor environment variables.

        https://docs.apify.com/api/v2#/reference/actors/environment-variable-collection/get-list-of-environment-variables

        Returns:
            The list of available Actor environment variables.
        """
        result = self._list()
        return ListOfEnvVarsResponse.model_validate(result).data

    def create(
        self,
        *,
        is_secret: bool | None = None,
        name: str,
        value: str,
    ) -> EnvVar:
        """Create a new Actor environment variable.

        https://docs.apify.com/api/v2#/reference/actors/environment-variable-collection/create-environment-variable

        Args:
            is_secret: Whether the environment variable is secret or not.
            name: The name of the environment variable.
            value: The value of the environment variable.

        Returns:
            The created Actor environment variable.
        """
        actor_env_var_representation = get_actor_env_var_representation(
            is_secret=is_secret,
            name=name,
            value=value,
        )

        result = self._create(filter_none_values(actor_env_var_representation))
        return EnvVarResponse.model_validate(result).data


@docs_group('Resource clients')
class ActorEnvVarCollectionClientAsync(ResourceClientAsync):
    """Async sub-client for manipulating Actor env vars."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'env-vars')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def list(self) -> ListOfEnvVars:
        """List the available Actor environment variables.

        https://docs.apify.com/api/v2#/reference/actors/environment-variable-collection/get-list-of-environment-variables

        Returns:
            The list of available Actor environment variables.
        """
        result = await self._list()
        return ListOfEnvVarsResponse.model_validate(result).data

    async def create(
        self,
        *,
        is_secret: bool | None = None,
        name: str,
        value: str,
    ) -> EnvVar:
        """Create a new Actor environment variable.

        https://docs.apify.com/api/v2#/reference/actors/environment-variable-collection/create-environment-variable

        Args:
            is_secret: Whether the environment variable is secret or not.
            name: The name of the environment variable.
            value: The value of the environment variable.

        Returns:
            The created Actor environment variable.
        """
        actor_env_var_representation = get_actor_env_var_representation(
            is_secret=is_secret,
            name=name,
            value=value,
        )

        result = await self._create(filter_none_values(actor_env_var_representation))
        return EnvVarResponse.model_validate(result).data
