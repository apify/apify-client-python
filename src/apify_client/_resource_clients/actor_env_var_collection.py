from __future__ import annotations

from typing import Any

from apify_client._models import EnvVar, GetListOfEnvVarsResponse, ListOfEnvVars
from apify_client._resource_clients.actor_env_var import get_actor_env_var_representation
from apify_client._resource_clients.base import ResourceCollectionClient, ResourceCollectionClientAsync
from apify_client._utils import filter_out_none_values_recursively, response_to_dict


class ActorEnvVarCollectionClient(ResourceCollectionClient):
    """Sub-client for manipulating actor env vars."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'env-vars')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def list(self) -> ListOfEnvVars:
        """List the available actor environment variables.

        https://docs.apify.com/api/v2#/reference/actors/environment-variable-collection/get-list-of-environment-variables

        Returns:
            The list of available actor environment variables.
        """
        response = self.http_client.call(
            url=self._url(),
            method='GET',
            params=self._params(),
        )
        data = response_to_dict(response)
        return GetListOfEnvVarsResponse.model_validate(data).data

    def create(
        self,
        *,
        is_secret: bool | None = None,
        name: str,
        value: str,
    ) -> EnvVar:
        """Create a new actor environment variable.

        https://docs.apify.com/api/v2#/reference/actors/environment-variable-collection/create-environment-variable

        Args:
            is_secret: Whether the environment variable is secret or not.
            name: The name of the environment variable.
            value: The value of the environment variable.

        Returns:
            The created actor environment variable.
        """
        actor_env_var_representation = get_actor_env_var_representation(
            is_secret=is_secret,
            name=name,
            value=value,
        )

        result = self._create(filter_out_none_values_recursively(actor_env_var_representation))
        return EnvVar.model_validate(result)


class ActorEnvVarCollectionClientAsync(ResourceCollectionClientAsync):
    """Async sub-client for manipulating actor env vars."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'env-vars')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def list(self) -> ListOfEnvVars:
        """List the available actor environment variables.

        https://docs.apify.com/api/v2#/reference/actors/environment-variable-collection/get-list-of-environment-variables

        Returns:
            The list of available actor environment variables.
        """
        response = await self.http_client.call(
            url=self._url(),
            method='GET',
            params=self._params(),
        )
        data = response_to_dict(response)
        return GetListOfEnvVarsResponse.model_validate(data).data

    async def create(
        self,
        *,
        is_secret: bool | None = None,
        name: str,
        value: str,
    ) -> EnvVar:
        """Create a new actor environment variable.

        https://docs.apify.com/api/v2#/reference/actors/environment-variable-collection/create-environment-variable

        Args:
            is_secret: Whether the environment variable is secret or not.
            name: The name of the environment variable.
            value: The value of the environment variable.

        Returns:
            The created actor environment variable.
        """
        actor_env_var_representation = get_actor_env_var_representation(
            is_secret=is_secret,
            name=name,
            value=value,
        )

        result = await self._create(filter_out_none_values_recursively(actor_env_var_representation))
        return EnvVar.model_validate(result)
