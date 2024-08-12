from __future__ import annotations

from typing import Any

from apify_shared.utils import filter_out_none_values_recursively, ignore_docs

from apify_client.clients.base import ResourceClient, ResourceClientAsync


def get_actor_env_var_representation(
    *,
    is_secret: bool | None = None,
    name: str | None = None,
    value: str | None = None,
) -> dict:
    """Returns an environment variable representation of the Actor in a dictionary."""
    return {
        'isSecret': is_secret,
        'name': name,
        'value': value,
    }


class ActorEnvVarClient(ResourceClient):
    """Sub-client for manipulating a single Actor environment variable."""

    @ignore_docs
    def __init__(self: ActorEnvVarClient, *args: Any, **kwargs: Any) -> None:
        """Initialize the ActorEnvVarClient."""
        resource_path = kwargs.pop('resource_path', 'env-vars')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def get(self: ActorEnvVarClient) -> dict | None:
        """Return information about the Actor environment variable.

        https://docs.apify.com/api/v2#/reference/actors/environment-variable-object/get-environment-variable

        Returns:
            dict, optional: The retrieved Actor environment variable data
        """
        return self._get()

    def update(
        self: ActorEnvVarClient,
        *,
        is_secret: bool | None = None,
        name: str,
        value: str,
    ) -> dict:
        """Update the Actor environment variable with specified fields.

        https://docs.apify.com/api/v2#/reference/actors/environment-variable-object/update-environment-variable

        Args:
            is_secret (bool, optional): Whether the environment variable is secret or not
            name (str): The name of the environment variable
            value (str): The value of the environment variable

        Returns:
            dict: The updated Actor environment variable
        """
        actor_env_var_representation = get_actor_env_var_representation(
            is_secret=is_secret,
            name=name,
            value=value,
        )

        return self._update(filter_out_none_values_recursively(actor_env_var_representation))

    def delete(self: ActorEnvVarClient) -> None:
        """Delete the Actor environment variable.

        https://docs.apify.com/api/v2#/reference/actors/environment-variable-object/delete-environment-variable
        """
        return self._delete()


class ActorEnvVarClientAsync(ResourceClientAsync):
    """Async sub-client for manipulating a single Actor environment variable."""

    @ignore_docs
    def __init__(self: ActorEnvVarClientAsync, *args: Any, **kwargs: Any) -> None:
        """Initialize the ActorEnvVarClientAsync."""
        resource_path = kwargs.pop('resource_path', 'env-vars')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def get(self: ActorEnvVarClientAsync) -> dict | None:
        """Return information about the Actor environment variable.

        https://docs.apify.com/api/v2#/reference/actors/environment-variable-object/get-environment-variable

        Returns:
            dict, optional: The retrieved Actor environment variable data
        """
        return await self._get()

    async def update(
        self: ActorEnvVarClientAsync,
        *,
        is_secret: bool | None = None,
        name: str,
        value: str,
    ) -> dict:
        """Update the Actor environment variable with specified fields.

        https://docs.apify.com/api/v2#/reference/actors/environment-variable-object/update-environment-variable

        Args:
            is_secret (bool, optional): Whether the environment variable is secret or not
            name (str): The name of the environment variable
            value (str): The value of the environment variable

        Returns:
            dict: The updated Actor environment variable
        """
        actor_env_var_representation = get_actor_env_var_representation(
            is_secret=is_secret,
            name=name,
            value=value,
        )

        return await self._update(filter_out_none_values_recursively(actor_env_var_representation))

    async def delete(self: ActorEnvVarClientAsync) -> None:
        """Delete the Actor environment variable.

        https://docs.apify.com/api/v2#/reference/actors/environment-variable-object/delete-environment-variable
        """
        return await self._delete()
