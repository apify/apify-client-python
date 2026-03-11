from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import TypeAdapter

from apify_client._docs import docs_group
from apify_client._models import (
    CreateOrUpdateVersionRequest,
    EnvVar,
    ListOfVersions,
    ListOfVersionsResponse,
    SourceCodeFile,
    SourceCodeFolder,
    Version,
    VersionResponse,
    VersionSourceType,
)
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync

if TYPE_CHECKING:
    from apify_client._types import Timeout


_source_file_list_adapter = TypeAdapter(list[SourceCodeFile | SourceCodeFolder])


@docs_group('Resource clients')
class ActorVersionCollectionClient(ResourceClient):
    """Sub-client for the Actor version collection.

    Provides methods to manage Actor versions, e.g. list or create them. Obtain an instance via an appropriate method
    on the `ActorClient` class.
    """

    def __init__(
        self,
        *,
        resource_path: str = 'versions',
        **kwargs: Any,
    ) -> None:
        super().__init__(
            resource_path=resource_path,
            **kwargs,
        )

    def list(self, *, timeout: Timeout = 'short') -> ListOfVersions:
        """List the available Actor versions.

        https://docs.apify.com/api/v2#/reference/actors/version-collection/get-list-of-versions

        Args:
            timeout: Timeout for the API HTTP request.

        Returns:
            The list of available Actor versions.
        """
        result = self._list(timeout=timeout)
        return ListOfVersionsResponse.model_validate(result).data

    def create(
        self,
        *,
        version_number: str,
        build_tag: str | None = None,
        env_vars: list[dict[str, Any]] | None = None,  # ty: ignore[invalid-type-form]
        apply_env_vars_to_build: bool | None = None,
        source_type: VersionSourceType,
        source_files: list[dict[str, Any]] | None = None,  # ty: ignore[invalid-type-form]
        git_repo_url: str | None = None,
        tarball_url: str | None = None,
        github_gist_url: str | None = None,
        timeout: Timeout = 'short',
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
            timeout: Timeout for the API HTTP request.

        Returns:
            The created Actor version.
        """
        version_fields = CreateOrUpdateVersionRequest(
            version_number=version_number,
            build_tag=build_tag,
            env_vars=[EnvVar.model_validate(v) for v in env_vars] if env_vars else None,
            apply_env_vars_to_build=apply_env_vars_to_build,
            source_type=source_type,
            source_files=_source_file_list_adapter.validate_python(source_files) if source_files else None,
            git_repo_url=git_repo_url,
            tarball_url=tarball_url,
            github_gist_url=github_gist_url,
        )
        result = self._create(timeout=timeout, **version_fields.model_dump(by_alias=True, exclude_none=True))
        return VersionResponse.model_validate(result).data


@docs_group('Resource clients')
class ActorVersionCollectionClientAsync(ResourceClientAsync):
    """Sub-client for the Actor version collection.

    Provides methods to manage Actor versions, e.g. list or create them. Obtain an instance via an appropriate method
    on the `ActorClientAsync` class.
    """

    def __init__(
        self,
        *,
        resource_path: str = 'versions',
        **kwargs: Any,
    ) -> None:
        super().__init__(
            resource_path=resource_path,
            **kwargs,
        )

    async def list(self, *, timeout: Timeout = 'short') -> ListOfVersions:
        """List the available Actor versions.

        https://docs.apify.com/api/v2#/reference/actors/version-collection/get-list-of-versions

        Args:
            timeout: Timeout for the API HTTP request.

        Returns:
            The list of available Actor versions.
        """
        result = await self._list(timeout=timeout)
        return ListOfVersionsResponse.model_validate(result).data

    async def create(
        self,
        *,
        version_number: str,
        build_tag: str | None = None,
        env_vars: list[dict[str, Any]] | None = None,  # ty: ignore[invalid-type-form]
        apply_env_vars_to_build: bool | None = None,
        source_type: VersionSourceType,
        source_files: list[dict[str, Any]] | None = None,  # ty: ignore[invalid-type-form]
        git_repo_url: str | None = None,
        tarball_url: str | None = None,
        github_gist_url: str | None = None,
        timeout: Timeout = 'short',
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
            timeout: Timeout for the API HTTP request.

        Returns:
            The created Actor version.
        """
        version_fields = CreateOrUpdateVersionRequest(
            version_number=version_number,
            build_tag=build_tag,
            env_vars=[EnvVar.model_validate(v) for v in env_vars] if env_vars else None,
            apply_env_vars_to_build=apply_env_vars_to_build,
            source_type=source_type,
            source_files=_source_file_list_adapter.validate_python(source_files) if source_files else None,
            git_repo_url=git_repo_url,
            tarball_url=tarball_url,
            github_gist_url=github_gist_url,
        )
        result = await self._create(timeout=timeout, **version_fields.model_dump(by_alias=True, exclude_none=True))
        return VersionResponse.model_validate(result).data
