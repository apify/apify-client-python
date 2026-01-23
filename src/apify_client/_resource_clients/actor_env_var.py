from __future__ import annotations

from typing import Any

from apify_client._models import EnvVar, GetEnvVarResponse
from apify_client._resource_clients.base import ResourceClient, ResourceClientAsync
from apify_client._utils import filter_out_none_values_recursively


def get_actor_env_var_representation(
    *,
    is_secret: bool | None = None,
    name: str | None = None,
    value: str | None = None,
) -> dict:
    """Return an environment variable representation of the Actor in a dictionary."""
    return {
        'isSecret': is_secret,
        'name': name,
        'value': value,
    }


class ActorEnvVarClient(ResourceClient):
    """Sub-client for manipulating a single Actor environment variable."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'env-vars')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def get(self) -> EnvVar | None:
        """Return information about the Actor environment variable.

        https://docs.apify.com/api/v2#/reference/actors/environment-variable-object/get-environment-variable

        Returns:
            The retrieved Actor environment variable data.
        """
        result = self._get()
        return GetEnvVarResponse.model_validate(result).data if result is not None else None

    def update(
        self,
        *,
        is_secret: bool | None = None,
        name: str,
        value: str,
    ) -> EnvVar:
        """Update the Actor environment variable with specified fields.

        https://docs.apify.com/api/v2#/reference/actors/environment-variable-object/update-environment-variable

        Args:
            is_secret: Whether the environment variable is secret or not.
            name: The name of the environment variable.
            value: The value of the environment variable.

        Returns:
            The updated Actor environment variable.
        """
        actor_env_var_representation = get_actor_env_var_representation(
            is_secret=is_secret,
            name=name,
            value=value,
        )

        result = self._update(filter_out_none_values_recursively(actor_env_var_representation))
        return GetEnvVarResponse.model_validate(result).data

    def delete(self) -> None:
        """Delete the Actor environment variable.

        https://docs.apify.com/api/v2#/reference/actors/environment-variable-object/delete-environment-variable
        """
        return self._delete()


class ActorEnvVarClientAsync(ResourceClientAsync):
    """Async sub-client for manipulating a single Actor environment variable."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'env-vars')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def get(self) -> EnvVar | None:
        """Return information about the Actor environment variable.

        https://docs.apify.com/api/v2#/reference/actors/environment-variable-object/get-environment-variable

        Returns:
            The retrieved Actor environment variable data.
        """
        result = await self._get()
        return GetEnvVarResponse.model_validate(result).data if result is not None else None

    async def update(
        self,
        *,
        is_secret: bool | None = None,
        name: str,
        value: str,
    ) -> EnvVar:
        """Update the Actor environment variable with specified fields.

        https://docs.apify.com/api/v2#/reference/actors/environment-variable-object/update-environment-variable

        Args:
            is_secret: Whether the environment variable is secret or not.
            name: The name of the environment variable.
            value: The value of the environment variable.

        Returns:
            The updated Actor environment variable.
        """
        actor_env_var_representation = get_actor_env_var_representation(
            is_secret=is_secret,
            name=name,
            value=value,
        )

        result = await self._update(filter_out_none_values_recursively(actor_env_var_representation))
        return GetEnvVarResponse.model_validate(result).data

    async def delete(self) -> None:
        """Delete the Actor environment variable.

        https://docs.apify.com/api/v2#/reference/actors/environment-variable-object/delete-environment-variable
        """
        return await self._delete()
