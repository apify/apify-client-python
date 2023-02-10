from typing import Any, Dict, Optional

from ..._utils import _filter_out_none_values_recursively, ignore_docs
from ..base import ResourceClient, ResourceClientAsync


def _get_actor_env_var_representation(
    *,
    is_secret: Optional[bool] = None,
    name: Optional[str] = None,
    value: Optional[str] = None,
) -> Dict:
    return {
        'isSecret': is_secret,
        'name': name,
        'value': value,
    }


class ActorEnvVarClient(ResourceClient):
    """Sub-client for manipulating a single actor environment variable."""

    @ignore_docs
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the ActorEnvVarClient."""
        resource_path = kwargs.pop('resource_path', 'env-vars')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def get(self) -> Optional[Dict]:
        """Return information about the actor environment variable.

        https://docs.apify.com/api/v2#/reference/actors/environment-variable-object/get-environment-variable

        Returns:
            dict, optional: The retrieved actor environment variable data
        """
        return self._get()

    def update(
        self,
        *,
        is_secret: Optional[bool] = None,
        name: str,
        value: str,
    ) -> Dict:
        """Update the actor environment variable with specified fields.

        https://docs.apify.com/api/v2#/reference/actors/environment-variable-object/update-environment-variable

        Args:
            is_secret (bool, optional): Whether the environment variable is secret or not
            name (str): The name of the environment variable
            value (str): The value of the environment variable

        Returns:
            dict: The updated actor environment variable
        """
        actor_env_var_representation = _get_actor_env_var_representation(
            is_secret=is_secret,
            name=name,
            value=value,
        )

        return self._update(_filter_out_none_values_recursively(actor_env_var_representation))

    def delete(self) -> None:
        """Delete the actor environment variable.

        https://docs.apify.com/api/v2#/reference/actors/environment-variable-object/delete-environment-variable
        """
        return self._delete()


class ActorEnvVarClientAsync(ResourceClientAsync):
    """Async sub-client for manipulating a single actor environment variable."""

    @ignore_docs
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the ActorEnvVarClientAsync."""
        resource_path = kwargs.pop('resource_path', 'env-vars')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def get(self) -> Optional[Dict]:
        """Return information about the actor environment variable.

        https://docs.apify.com/api/v2#/reference/actors/environment-variable-object/get-environment-variable

        Returns:
            dict, optional: The retrieved actor environment variable data
        """
        return await self._get()

    async def update(
        self,
        *,
        is_secret: Optional[bool] = None,
        name: str,
        value: str,
    ) -> Dict:
        """Update the actor environment variable with specified fields.

        https://docs.apify.com/api/v2#/reference/actors/environment-variable-object/update-environment-variable

        Args:
            is_secret (bool, optional): Whether the environment variable is secret or not
            name (str): The name of the environment variable
            value (str): The value of the environment variable

        Returns:
            dict: The updated actor environment variable
        """
        actor_env_var_representation = _get_actor_env_var_representation(
            is_secret=is_secret,
            name=name,
            value=value,
        )

        return await self._update(_filter_out_none_values_recursively(actor_env_var_representation))

    async def delete(self) -> None:
        """Delete the actor environment variable.

        https://docs.apify.com/api/v2#/reference/actors/environment-variable-object/delete-environment-variable
        """
        return await self._delete()
