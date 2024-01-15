from __future__ import annotations

from typing import TYPE_CHECKING, Any

from apify_shared.utils import filter_out_none_values_recursively, ignore_docs

from apify_client.clients.base import ResourceCollectionClient, ResourceCollectionClientAsync
from apify_client.clients.resource_clients.actor_env_var import get_actor_env_var_representation

if TYPE_CHECKING:
    from apify_shared.models import ListPage


class ActorEnvVarCollectionClient(ResourceCollectionClient):
    """Sub-client for manipulating actor env vars."""

    @ignore_docs
    def __init__(self: ActorEnvVarCollectionClient, *args: Any, **kwargs: Any) -> None:
        """Initialize the ActorEnvVarCollectionClient with the passed arguments."""
        resource_path = kwargs.pop('resource_path', 'env-vars')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def list(self: ActorEnvVarCollectionClient) -> ListPage[dict]:
        """List the available actor environment variables.

        https://docs.apify.com/api/v2#/reference/actors/environment-variable-collection/get-list-of-environment-variables

        Returns:
            ListPage: The list of available actor environment variables.
        """
        return self._list()

    def create(
        self: ActorEnvVarCollectionClient,
        *,
        is_secret: bool | None = None,
        name: str,
        value: str,
    ) -> dict:
        """Create a new actor environment variable.

        https://docs.apify.com/api/v2#/reference/actors/environment-variable-collection/create-environment-variable

        Args:
            is_secret (bool, optional): Whether the environment variable is secret or not
            name (str): The name of the environment variable
            value (str): The value of the environment variable

        Returns:
            dict: The created actor environment variable
        """
        actor_env_var_representation = get_actor_env_var_representation(
            is_secret=is_secret,
            name=name,
            value=value,
        )

        return self._create(filter_out_none_values_recursively(actor_env_var_representation))


class ActorEnvVarCollectionClientAsync(ResourceCollectionClientAsync):
    """Async sub-client for manipulating actor env vars."""

    @ignore_docs
    def __init__(self: ActorEnvVarCollectionClientAsync, *args: Any, **kwargs: Any) -> None:
        """Initialize the ActorEnvVarCollectionClientAsync with the passed arguments."""
        resource_path = kwargs.pop('resource_path', 'env-vars')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def list(self: ActorEnvVarCollectionClientAsync) -> ListPage[dict]:
        """List the available actor environment variables.

        https://docs.apify.com/api/v2#/reference/actors/environment-variable-collection/get-list-of-environment-variables

        Returns:
            ListPage: The list of available actor environment variables.
        """
        return await self._list()

    async def create(
        self: ActorEnvVarCollectionClientAsync,
        *,
        is_secret: bool | None = None,
        name: str,
        value: str,
    ) -> dict:
        """Create a new actor environment variable.

        https://docs.apify.com/api/v2#/reference/actors/environment-variable-collection/create-environment-variable

        Args:
            is_secret (bool, optional): Whether the environment variable is secret or not
            name (str): The name of the environment variable
            value (str): The value of the environment variable

        Returns:
            dict: The created actor environment variable
        """
        actor_env_var_representation = get_actor_env_var_representation(
            is_secret=is_secret,
            name=name,
            value=value,
        )

        return await self._create(filter_out_none_values_recursively(actor_env_var_representation))
