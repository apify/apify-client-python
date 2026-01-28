from __future__ import annotations

from typing import Any

from apify_client._models import GetVersionResponse, Version, VersionSourceType
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync
from apify_client._resource_clients.actor_env_var import ActorEnvVarClient, ActorEnvVarClientAsync
from apify_client._resource_clients.actor_env_var_collection import (
    ActorEnvVarCollectionClient,
    ActorEnvVarCollectionClientAsync,
)
from apify_client._utils import catch_not_found_or_throw, enum_to_value, filter_none_values, response_to_dict
from apify_client.errors import ApifyApiError


def _get_actor_version_representation(
    *,
    version_number: str | None = None,
    build_tag: str | None = None,
    env_vars: list[dict] | None = None,
    apply_env_vars_to_build: bool | None = None,
    source_type: VersionSourceType | None = None,
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
        'sourceType': enum_to_value(source_type),
        'sourceFiles': source_files,
        'gitRepoUrl': git_repo_url,
        'tarballUrl': tarball_url,
        'gitHubGistUrl': github_gist_url,
    }


class ActorVersionClient(ResourceClient):
    """Sub-client for manipulating a single Actor version."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'versions')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def get(self) -> Version | None:
        """Return information about the Actor version.

        https://docs.apify.com/api/v2#/reference/actors/version-object/get-version

        Returns:
            The retrieved Actor version data.
        """
        try:
            response = self._http_client.call(
                url=self._build_url(),
                method='GET',
                params=self._build_params(),
            )
            result = response_to_dict(response)
            return GetVersionResponse.model_validate(result).data
        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)
            return None

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
        cleaned = filter_none_values(actor_version_representation)

        response = self._http_client.call(
            url=self._build_url(),
            method='PUT',
            params=self._build_params(),
            json=cleaned,
        )
        result = response_to_dict(response)
        return GetVersionResponse.model_validate(result).data

    def delete(self) -> None:
        """Delete the Actor version.

        https://docs.apify.com/api/v2#/reference/actors/version-object/delete-version
        """
        try:
            self._http_client.call(
                url=self._build_url(),
                method='DELETE',
                params=self._build_params(),
            )
        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

    def env_vars(self) -> ActorEnvVarCollectionClient:
        """Retrieve a client for the environment variables of this Actor version."""
        return ActorEnvVarCollectionClient(**self._nested_client_config())

    def env_var(self, env_var_name: str) -> ActorEnvVarClient:
        """Retrieve the client for the specified environment variable of this Actor version.

        Args:
            env_var_name: The name of the environment variable for which to retrieve the resource client.

        Returns:
            The resource client for the specified Actor environment variable.
        """
        return ActorEnvVarClient(**self._nested_client_config(resource_id=env_var_name))


class ActorVersionClientAsync(ResourceClientAsync):
    """Async sub-client for manipulating a single Actor version."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'versions')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def get(self) -> Version | None:
        """Return information about the Actor version.

        https://docs.apify.com/api/v2#/reference/actors/version-object/get-version

        Returns:
            The retrieved Actor version data.
        """
        try:
            response = await self._http_client.call(
                url=self._build_url(),
                method='GET',
                params=self._build_params(),
            )
            result = response_to_dict(response)
            return GetVersionResponse.model_validate(result).data
        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)
            return None

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
        cleaned = filter_none_values(actor_version_representation)

        response = await self._http_client.call(
            url=self._build_url(),
            method='PUT',
            params=self._build_params(),
            json=cleaned,
        )
        result = response_to_dict(response)
        return GetVersionResponse.model_validate(result).data

    async def delete(self) -> None:
        """Delete the Actor version.

        https://docs.apify.com/api/v2#/reference/actors/version-object/delete-version
        """
        try:
            await self._http_client.call(
                url=self._build_url(),
                method='DELETE',
                params=self._build_params(),
            )
        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

    def env_vars(self) -> ActorEnvVarCollectionClientAsync:
        """Retrieve a client for the environment variables of this Actor version."""
        return ActorEnvVarCollectionClientAsync(**self._nested_client_config())

    def env_var(self, env_var_name: str) -> ActorEnvVarClientAsync:
        """Retrieve the client for the specified environment variable of this Actor version.

        Args:
            env_var_name: The name of the environment variable for which to retrieve the resource client.

        Returns:
            The resource client for the specified Actor environment variable.
        """
        return ActorEnvVarClientAsync(**self._nested_client_config(resource_id=env_var_name))
