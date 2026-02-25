from __future__ import annotations

from typing import TYPE_CHECKING, Any

from apify_client._docs import docs_group
from apify_client._models import Version, VersionResponse, VersionSourceType
from apify_client._representations import get_actor_version_repr
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync
from apify_client._utils import filter_none_values

if TYPE_CHECKING:
    from apify_client._resource_clients import (
        ActorEnvVarClient,
        ActorEnvVarClientAsync,
        ActorEnvVarCollectionClient,
        ActorEnvVarCollectionClientAsync,
    )


@docs_group('Resource clients')
class ActorVersionClient(ResourceClient):
    """Sub-client for managing a specific Actor version.

    Provides methods to manage a specific Actor version, e.g. get, update, or delete it. Obtain an instance via an
    appropriate method on the `ActorClient` class.
    """

    def __init__(
        self,
        *,
        resource_id: str,
        resource_path: str = 'versions',
        **kwargs: Any,
    ) -> None:
        super().__init__(
            resource_id=resource_id,
            resource_path=resource_path,
            **kwargs,
        )

    def get(self) -> Version | None:
        """Return information about the Actor version.

        https://docs.apify.com/api/v2#/reference/actors/version-object/get-version

        Returns:
            The retrieved Actor version data.
        """
        result = self._get()
        if result is None:
            return None
        return VersionResponse.model_validate(result).data

    def update(
        self,
        *,
        build_tag: str | None = None,
        env_vars: list[dict] | None = None,
        apply_env_vars_to_build: bool | None = None,
        source_type: VersionSourceType | None = None,
        source_files: list[dict] | None = None,
        git_repo_url: str | None = None,
        tarball_url: str | None = None,
        github_gist_url: str | None = None,
    ) -> Version:
        """Update the Actor version with specified fields.

        https://docs.apify.com/api/v2#/reference/actors/version-object/update-version

        Args:
            build_tag: Tag that is automatically set to the latest successful build of the current version.
            env_vars: Environment variables that will be available to the Actor run process, and optionally
                also to the build process. See the API docs for their exact structure.
            apply_env_vars_to_build: Whether the environment variables specified for the Actor run will also
                be set to the Actor build process.
            source_type: What source type is the Actor version using.
            source_files: Source code comprised of multiple files, each an item of the array. Required when
                `source_type` is `VersionSourceType.SOURCE_FILES`. See the API docs for the exact structure.
            git_repo_url: The URL of a Git repository from which the source code will be cloned.
                Required when `source_type` is `VersionSourceType.GIT_REPO`.
            tarball_url: The URL of a tarball or a zip archive from which the source code will be downloaded.
                Required when `source_type` is `VersionSourceType.TARBALL`.
            github_gist_url: The URL of a GitHub Gist from which the source will be downloaded.
                Required when `source_type` is `VersionSourceType.GITHUB_GIST`.

        Returns:
            The updated Actor version.
        """
        actor_version_representation = get_actor_version_repr(
            build_tag=build_tag,
            env_vars=env_vars,
            apply_env_vars_to_build=apply_env_vars_to_build,
            source_type=source_type,
            source_files=source_files,
            git_repo_url=git_repo_url,
            tarball_url=tarball_url,
            github_gist_url=github_gist_url,
        )
        cleaned = filter_none_values(actor_version_representation)

        result = self._update(cleaned)
        return VersionResponse.model_validate(result).data

    def delete(self) -> None:
        """Delete the Actor version.

        https://docs.apify.com/api/v2#/reference/actors/version-object/delete-version
        """
        self._delete()

    def env_vars(self) -> ActorEnvVarCollectionClient:
        """Retrieve a client for the environment variables of this Actor version."""
        return self._client_registry.actor_env_var_collection_client(**self._base_client_kwargs)

    def env_var(self, env_var_name: str) -> ActorEnvVarClient:
        """Retrieve the client for the specified environment variable of this Actor version.

        Args:
            env_var_name: The name of the environment variable for which to retrieve the resource client.

        Returns:
            The resource client for the specified Actor environment variable.
        """
        return self._client_registry.actor_env_var_client(
            resource_id=env_var_name,
            **self._base_client_kwargs,
        )


@docs_group('Resource clients')
class ActorVersionClientAsync(ResourceClientAsync):
    """Sub-client for managing a specific Actor version.

    Provides methods to manage a specific Actor version, e.g. get, update, or delete it. Obtain an instance via an
    appropriate method on the `ActorClientAsync` class.
    """

    def __init__(
        self,
        *,
        resource_id: str,
        resource_path: str = 'versions',
        **kwargs: Any,
    ) -> None:
        super().__init__(
            resource_id=resource_id,
            resource_path=resource_path,
            **kwargs,
        )

    async def get(self) -> Version | None:
        """Return information about the Actor version.

        https://docs.apify.com/api/v2#/reference/actors/version-object/get-version

        Returns:
            The retrieved Actor version data.
        """
        result = await self._get()
        if result is None:
            return None
        return VersionResponse.model_validate(result).data

    async def update(
        self,
        *,
        build_tag: str | None = None,
        env_vars: list[dict] | None = None,
        apply_env_vars_to_build: bool | None = None,
        source_type: VersionSourceType | None = None,
        source_files: list[dict] | None = None,
        git_repo_url: str | None = None,
        tarball_url: str | None = None,
        github_gist_url: str | None = None,
    ) -> Version:
        """Update the Actor version with specified fields.

        https://docs.apify.com/api/v2#/reference/actors/version-object/update-version

        Args:
            build_tag: Tag that is automatically set to the latest successful build of the current version.
            env_vars: Environment variables that will be available to the Actor run process, and optionally
                also to the build process. See the API docs for their exact structure.
            apply_env_vars_to_build: Whether the environment variables specified for the Actor run will also
                be set to the Actor build process.
            source_type: What source type is the Actor version using.
            source_files: Source code comprised of multiple files, each an item of the array. Required when
                `source_type` is `VersionSourceType.SOURCE_FILES`. See the API docs for the exact structure.
            git_repo_url: The URL of a Git repository from which the source code will be cloned.
                Required when `source_type` is `VersionSourceType.GIT_REPO`.
            tarball_url: The URL of a tarball or a zip archive from which the source code will be downloaded.
                Required when `source_type` is `VersionSourceType.TARBALL`.
            github_gist_url: The URL of a GitHub Gist from which the source will be downloaded.
                Required when `source_type` is `VersionSourceType.GITHUB_GIST`.

        Returns:
            The updated Actor version.
        """
        actor_version_representation = get_actor_version_repr(
            build_tag=build_tag,
            env_vars=env_vars,
            apply_env_vars_to_build=apply_env_vars_to_build,
            source_type=source_type,
            source_files=source_files,
            git_repo_url=git_repo_url,
            tarball_url=tarball_url,
            github_gist_url=github_gist_url,
        )
        cleaned = filter_none_values(actor_version_representation)

        result = await self._update(cleaned)
        return VersionResponse.model_validate(result).data

    async def delete(self) -> None:
        """Delete the Actor version.

        https://docs.apify.com/api/v2#/reference/actors/version-object/delete-version
        """
        await self._delete()

    def env_vars(self) -> ActorEnvVarCollectionClientAsync:
        """Retrieve a client for the environment variables of this Actor version."""
        return self._client_registry.actor_env_var_collection_client(**self._base_client_kwargs)

    def env_var(self, env_var_name: str) -> ActorEnvVarClientAsync:
        """Retrieve the client for the specified environment variable of this Actor version.

        Args:
            env_var_name: The name of the environment variable for which to retrieve the resource client.

        Returns:
            The resource client for the specified Actor environment variable.
        """
        return self._client_registry.actor_env_var_client(
            resource_id=env_var_name,
            **self._base_client_kwargs,
        )
