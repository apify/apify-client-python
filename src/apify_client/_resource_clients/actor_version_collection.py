from __future__ import annotations

from typing import Any

from apify_client._models import (
    GetListOfVersionsResponse,
    GetVersionResponse,
    ListOfVersions,
    Version,
    VersionSourceType,
)
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync
from apify_client._resource_clients.actor_version import _get_actor_version_representation
from apify_client._utils import filter_none_values, response_to_dict


class ActorVersionCollectionClient(ResourceClient):
    """Sub-client for manipulating Actor versions."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'versions')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def list(self) -> ListOfVersions:
        """List the available Actor versions.

        https://docs.apify.com/api/v2#/reference/actors/version-collection/get-list-of-versions

        Returns:
            The list of available Actor versions.
        """
        response = self.http_client.call(
            url=self._url(),
            method='GET',
            params=self._build_params(),
        )
        response_as_dict = response_to_dict(response)
        return GetListOfVersionsResponse.model_validate(response_as_dict).data

    def create(
        self,
        *,
        version_number: str,
        build_tag: str | None = None,
        env_vars: list[dict] | None = None,  # ty: ignore[invalid-type-form]
        apply_env_vars_to_build: bool | None = None,
        source_type: VersionSourceType,
        source_files: list[dict] | None = None,  # ty: ignore[invalid-type-form]
        git_repo_url: str | None = None,
        tarball_url: str | None = None,
        github_gist_url: str | None = None,
    ) -> Version:
        """Create a new Actor version.

        https://docs.apify.com/api/v2#/reference/actors/version-collection/create-version

        Args:
            version_number: Major and minor version of the Actor (e.g. `1.0`).
            build_tag: Tag that is automatically set to the latest successful build of the current version.
            env_vars: Environment variables that will be available to the Actor run process, and optionally
                also to the build process. See the API docs for their exact structure.
            apply_env_vars_to_build: Whether the environment variables specified for the Actor run will also
                be set to the Actor build process.
            source_type: What source type is the Actor version using.
            source_files: Source code comprised of multiple files, each an item of the array. Required
                when `source_type` is `VersionSourceType.SOURCE_FILES`. See the API docs for the exact structure.
            git_repo_url: The URL of a Git repository from which the source code will be cloned.
                Required when `source_type` is `VersionSourceType.GIT_REPO`.
            tarball_url: The URL of a tarball or a zip archive from which the source code will be downloaded.
                Required when `source_type` is `VersionSourceType.TARBALL`.
            github_gist_url: The URL of a GitHub Gist from which the source will be downloaded.
                Required when `source_type` is `VersionSourceType.GITHUB_GIST`.

        Returns:
            The created Actor version.
        """
        actor_version_representation = _get_actor_version_representation(
            version_number=version_number,
            build_tag=build_tag,
            env_vars=env_vars,
            apply_env_vars_to_build=apply_env_vars_to_build,
            source_type=source_type,
            source_files=source_files,
            git_repo_url=git_repo_url,
            tarball_url=tarball_url,
            github_gist_url=github_gist_url,
        )

        response = self.http_client.call(
            url=self._url(),
            method='POST',
            params=self._build_params(),
            json=filter_none_values(actor_version_representation),
        )

        result = response_to_dict(response)
        return GetVersionResponse.model_validate(result).data


class ActorVersionCollectionClientAsync(ResourceClientAsync):
    """Async sub-client for manipulating Actor versions."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'versions')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def list(self) -> ListOfVersions:
        """List the available Actor versions.

        https://docs.apify.com/api/v2#/reference/actors/version-collection/get-list-of-versions

        Returns:
            The list of available Actor versions.
        """
        response = await self.http_client.call(
            url=self._url(),
            method='GET',
            params=self._build_params(),
        )
        response_as_dict = response_to_dict(response)
        return GetListOfVersionsResponse.model_validate(response_as_dict).data

    async def create(
        self,
        *,
        version_number: str,
        build_tag: str | None = None,
        env_vars: list[dict] | None = None,  # ty: ignore[invalid-type-form]
        apply_env_vars_to_build: bool | None = None,
        source_type: VersionSourceType,
        source_files: list[dict] | None = None,  # ty: ignore[invalid-type-form]
        git_repo_url: str | None = None,
        tarball_url: str | None = None,
        github_gist_url: str | None = None,
    ) -> Version:
        """Create a new Actor version.

        https://docs.apify.com/api/v2#/reference/actors/version-collection/create-version

        Args:
            version_number: Major and minor version of the Actor (e.g. `1.0`).
            build_tag: Tag that is automatically set to the latest successful build of the current version.
            env_vars: Environment variables that will be available to the Actor run process, and optionally
                also to the build process. See the API docs for their exact structure.
            apply_env_vars_to_build: Whether the environment variables specified for the Actor run will also
                be set to the Actor build process.
            source_type: What source type is the Actor version using.
            source_files: Source code comprised of multiple files, each an item of the array. Required
                when `source_type` is `VersionSourceType.SOURCE_FILES`. See the API docs for the exact structure.
            git_repo_url: The URL of a Git repository from which the source code will be cloned.
                Required when `source_type` is `VersionSourceType.GIT_REPO`.
            tarball_url: The URL of a tarball or a zip archive from which the source code will be downloaded.
                Required when `source_type` is `VersionSourceType.TARBALL`.
            github_gist_url: The URL of a GitHub Gist from which the source will be downloaded.
                Required when `source_type` is `VersionSourceType.GITHUB_GIST`.

        Returns:
            The created Actor version.
        """
        actor_version_representation = _get_actor_version_representation(
            version_number=version_number,
            build_tag=build_tag,
            env_vars=env_vars,
            apply_env_vars_to_build=apply_env_vars_to_build,
            source_type=source_type,
            source_files=source_files,
            git_repo_url=git_repo_url,
            tarball_url=tarball_url,
            github_gist_url=github_gist_url,
        )

        response = await self.http_client.call(
            url=self._url(),
            method='POST',
            params=self._build_params(),
            json=filter_none_values(actor_version_representation),
        )

        result = response_to_dict(response)
        return GetVersionResponse.model_validate(result).data
