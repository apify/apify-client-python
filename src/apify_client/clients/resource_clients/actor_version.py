from __future__ import annotations

from typing import TYPE_CHECKING, Any

from apify_shared.utils import filter_out_none_values_recursively, ignore_docs, maybe_extract_enum_member_value

from apify_client.clients.base import ResourceClient, ResourceClientAsync
from apify_client.clients.resource_clients.actor_env_var import ActorEnvVarClient, ActorEnvVarClientAsync
from apify_client.clients.resource_clients.actor_env_var_collection import (
    ActorEnvVarCollectionClient,
    ActorEnvVarCollectionClientAsync,
)

if TYPE_CHECKING:
    from apify_shared.consts import ActorSourceType


def _get_actor_version_representation(
    *,
    version_number: str | None = None,
    build_tag: str | None = None,
    env_vars: list[dict] | None = None,
    apply_env_vars_to_build: bool | None = None,
    source_type: ActorSourceType | None = None,
    source_files: list[dict] | None = None,
    git_repo_url: str | None = None,
    tarball_url: str | None = None,
    github_gist_url: str | None = None,
) -> dict:
    return {
        'versionNumber': version_number,
        'buildTag': build_tag,
        'envVars': env_vars,
        'applyEnvVarsToBuild': apply_env_vars_to_build,
        'sourceType': maybe_extract_enum_member_value(source_type),
        'sourceFiles': source_files,
        'gitRepoUrl': git_repo_url,
        'tarballUrl': tarball_url,
        'gitHubGistUrl': github_gist_url,
    }


class ActorVersionClient(ResourceClient):
    """Sub-client for manipulating a single Actor version."""

    @ignore_docs
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'versions')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def get(self) -> dict | None:
        """Return information about the Actor version.

        https://docs.apify.com/api/v2#/reference/actors/version-object/get-version

        Returns:
            The retrieved Actor version data.
        """
        return self._get()

    def update(
        self,
        *,
        build_tag: str | None = None,
        env_vars: list[dict] | None = None,
        apply_env_vars_to_build: bool | None = None,
        source_type: ActorSourceType | None = None,
        source_files: list[dict] | None = None,
        git_repo_url: str | None = None,
        tarball_url: str | None = None,
        github_gist_url: str | None = None,
    ) -> dict:
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
                `source_type` is `ActorSourceType.SOURCE_FILES`. See the API docs for the exact structure.
            git_repo_url: The URL of a Git repository from which the source code will be cloned.
                Required when `source_type` is `ActorSourceType.GIT_REPO`.
            tarball_url: The URL of a tarball or a zip archive from which the source code will be downloaded.
                Required when `source_type` is `ActorSourceType.TARBALL`.
            github_gist_url: The URL of a GitHub Gist from which the source will be downloaded.
                Required when `source_type` is `ActorSourceType.GITHUB_GIST`.

        Returns:
            The updated Actor version.
        """
        actor_version_representation = _get_actor_version_representation(
            build_tag=build_tag,
            env_vars=env_vars,
            apply_env_vars_to_build=apply_env_vars_to_build,
            source_type=source_type,
            source_files=source_files,
            git_repo_url=git_repo_url,
            tarball_url=tarball_url,
            github_gist_url=github_gist_url,
        )

        return self._update(filter_out_none_values_recursively(actor_version_representation))

    def delete(self) -> None:
        """Delete the Actor version.

        https://docs.apify.com/api/v2#/reference/actors/version-object/delete-version
        """
        return self._delete()

    def env_vars(self) -> ActorEnvVarCollectionClient:
        """Retrieve a client for the environment variables of this Actor version."""
        return ActorEnvVarCollectionClient(**self._sub_resource_init_options())

    def env_var(self, env_var_name: str) -> ActorEnvVarClient:
        """Retrieve the client for the specified environment variable of this Actor version.

        Args:
            env_var_name: The name of the environment variable for which to retrieve the resource client.

        Returns:
            The resource client for the specified Actor environment variable.
        """
        return ActorEnvVarClient(**self._sub_resource_init_options(resource_id=env_var_name))


class ActorVersionClientAsync(ResourceClientAsync):
    """Async sub-client for manipulating a single Actor version."""

    @ignore_docs
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'versions')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def get(self) -> dict | None:
        """Return information about the Actor version.

        https://docs.apify.com/api/v2#/reference/actors/version-object/get-version

        Returns:
            The retrieved Actor version data.
        """
        return await self._get()

    async def update(
        self,
        *,
        build_tag: str | None = None,
        env_vars: list[dict] | None = None,
        apply_env_vars_to_build: bool | None = None,
        source_type: ActorSourceType | None = None,
        source_files: list[dict] | None = None,
        git_repo_url: str | None = None,
        tarball_url: str | None = None,
        github_gist_url: str | None = None,
    ) -> dict:
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
                `source_type` is `ActorSourceType.SOURCE_FILES`. See the API docs for the exact structure.
            git_repo_url: The URL of a Git repository from which the source code will be cloned.
                Required when `source_type` is `ActorSourceType.GIT_REPO`.
            tarball_url: The URL of a tarball or a zip archive from which the source code will be downloaded.
                Required when `source_type` is `ActorSourceType.TARBALL`.
            github_gist_url: The URL of a GitHub Gist from which the source will be downloaded.
                Required when `source_type` is `ActorSourceType.GITHUB_GIST`.

        Returns:
            The updated Actor version.
        """
        actor_version_representation = _get_actor_version_representation(
            build_tag=build_tag,
            env_vars=env_vars,
            apply_env_vars_to_build=apply_env_vars_to_build,
            source_type=source_type,
            source_files=source_files,
            git_repo_url=git_repo_url,
            tarball_url=tarball_url,
            github_gist_url=github_gist_url,
        )

        return await self._update(filter_out_none_values_recursively(actor_version_representation))

    async def delete(self) -> None:
        """Delete the Actor version.

        https://docs.apify.com/api/v2#/reference/actors/version-object/delete-version
        """
        return await self._delete()

    def env_vars(self) -> ActorEnvVarCollectionClientAsync:
        """Retrieve a client for the environment variables of this Actor version."""
        return ActorEnvVarCollectionClientAsync(**self._sub_resource_init_options())

    def env_var(self, env_var_name: str) -> ActorEnvVarClientAsync:
        """Retrieve the client for the specified environment variable of this Actor version.

        Args:
            env_var_name: The name of the environment variable for which to retrieve the resource client.

        Returns:
            The resource client for the specified Actor environment variable.
        """
        return ActorEnvVarClientAsync(**self._sub_resource_init_options(resource_id=env_var_name))
