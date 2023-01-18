from typing import Any, Dict, Optional

from ..._utils import ListPage, _filter_out_none_values_recursively, _make_async_docs
from ..base import ResourceCollectionClient, ResourceCollectionClientAsync
from .actor_env_var import _get_actor_env_var_representation


class ActorEnvVarCollectionClient(ResourceCollectionClient):
    """Sub-client for manipulating actor env vars."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the ActorEnvVarCollectionClient with the passed arguments."""
        resource_path = kwargs.pop('resource_path', 'env-vars')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def list(self) -> ListPage[Dict]:
        """List the available actor environment variables.

        https://docs.apify.com/api/v2#/reference/actors/environment-variable-collection/get-list-of-environment-variables

        Returns:
            ListPage: The list of available actor environment variables.
        """
        return self._list()

    def create(
        self,
        *,
        is_secret: Optional[bool] = None,
        name: str,
        value: str,
    ) -> Dict:
        """Create a new actor environment variable.

        https://docs.apify.com/api/v2#/reference/actors/environment-variable-collection/create-environment-variable

        Args:
            is_secret (bool, optional): Whether the environment variable is secret or not
            name (str): The name of the environment variable
            value (str): The value of the environment variable

        Returns:
            dict: The created actor environment variable
        """
        actor_env_var_representation = _get_actor_env_var_representation(
            is_secret=is_secret,
            name=name,
            value=value,
        )

        return self._create(_filter_out_none_values_recursively(actor_env_var_representation))


class ActorEnvVarCollectionClientAsync(ResourceCollectionClientAsync):
    """Async sub-client for manipulating actor env vars."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the ActorEnvVarCollectionClientAsync with the passed arguments."""
        resource_path = kwargs.pop('resource_path', 'env-vars')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    @_make_async_docs(src=ActorEnvVarCollectionClient.list)
    async def list(self) -> ListPage[Dict]:
        return await self._list()

    @_make_async_docs(src=ActorEnvVarCollectionClient.create)
    async def create(
        self,
        *,
        is_secret: Optional[bool] = None,
        name: str,
        value: str,
    ) -> Dict:
        actor_env_var_representation = _get_actor_env_var_representation(
            is_secret=is_secret,
            name=name,
            value=value,
        )

        return await self._create(_filter_out_none_values_recursively(actor_env_var_representation))
