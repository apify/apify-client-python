from __future__ import annotations

from typing import Any

from apify_client._models import EnvVar, GetEnvVarResponse, GetListOfEnvVarsResponse, ListOfEnvVars
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync
from apify_client._resource_clients.actor_env_var import get_actor_env_var_representation
from apify_client._utils import filter_none_values, response_to_dict


class ActorEnvVarCollectionClient(ResourceClient):
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
            params=self._build_params(),
        )
        response_as_dict = response_to_dict(response)
        return GetListOfEnvVarsResponse.model_validate(response_as_dict).data

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

        response = self.http_client.call(
            url=self._url(),
            method='POST',
            params=self._build_params(),
            json=filter_none_values(actor_env_var_representation),
        )

        result = response_to_dict(response)
        return GetEnvVarResponse.model_validate(result).data


class ActorEnvVarCollectionClientAsync(ResourceClientAsync):
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
            params=self._build_params(),
        )
        response_as_dict = response_to_dict(response)
        return GetListOfEnvVarsResponse.model_validate(response_as_dict).data

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

        response = await self.http_client.call(
            url=self._url(),
            method='POST',
            params=self._build_params(),
            json=filter_none_values(actor_env_var_representation),
        )

        result = response_to_dict(response)
        return GetEnvVarResponse.model_validate(result).data
