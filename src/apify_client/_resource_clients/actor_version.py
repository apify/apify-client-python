from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import TypeAdapter

from apify_client._docs import docs_group
from apify_client._models import (
    CreateOrUpdateVersionRequest,
    EnvVar,
    SourceCodeFile,
    SourceCodeFolder,
    Version,
    VersionResponse,
    VersionSourceType,
)
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync

if TYPE_CHECKING:
    from apify_client._resource_clients import (
        ActorEnvVarClient,
        ActorEnvVarClientAsync,
        ActorEnvVarCollectionClient,
        ActorEnvVarCollectionClientAsync,
    )
    from apify_client._types import Timeout

_source_file_list_adapter = TypeAdapter(list[SourceCodeFile | SourceCodeFolder])


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

    def get(self, *, timeout: Timeout = 'long') -> Version | None:
        """Return information about the Actor version.

        https://docs.apify.com/api/v2#/reference/actors/version-object/get-version

        Args:
            timeout: Timeout for the API HTTP request.

        Returns:
            The retrieved Actor version data.
        """
        result = self._get(timeout=timeout)
        if result is None:
            return None
        return VersionResponse.model_validate(result).data

    def update(
        self,
        *,
        build_tag: str | None = None,
        env_vars: list[dict[str, Any]] | None = None,
        apply_env_vars_to_build: bool | None = None,
        source_type: VersionSourceType | None = None,
        source_files: list[dict[str, Any]] | None = None,
        git_repo_url: str | None = None,
        tarball_url: str | None = None,
        github_gist_url: str | None = None,
        timeout: Timeout = 'long',
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
            timeout: Timeout for the API HTTP request.

        Returns:
            The updated Actor version.
        """
        version_fields = CreateOrUpdateVersionRequest(
            build_tag=build_tag,
            env_vars=[EnvVar.model_validate(v) for v in env_vars] if env_vars else None,
            apply_env_vars_to_build=apply_env_vars_to_build,
            source_type=source_type,
            source_files=_source_file_list_adapter.validate_python(source_files) if source_files else None,
            git_repo_url=git_repo_url,
            tarball_url=tarball_url,
            github_gist_url=github_gist_url,
        )
        result = self._update(timeout=timeout, **version_fields.model_dump(by_alias=True, exclude_none=True))
        return VersionResponse.model_validate(result).data

    def delete(self, *, timeout: Timeout = 'long') -> None:
        """Delete the Actor version.

        https://docs.apify.com/api/v2#/reference/actors/version-object/delete-version

        Args:
            timeout: Timeout for the API HTTP request.
        """
        self._delete(timeout=timeout)

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

    async def get(self, *, timeout: Timeout = 'long') -> Version | None:
        """Return information about the Actor version.

        https://docs.apify.com/api/v2#/reference/actors/version-object/get-version

        Args:
            timeout: Timeout for the API HTTP request.

        Returns:
            The retrieved Actor version data.
        """
        result = await self._get(timeout=timeout)
        if result is None:
            return None
        return VersionResponse.model_validate(result).data

    async def update(
        self,
        *,
        build_tag: str | None = None,
        env_vars: list[dict[str, Any]] | None = None,
        apply_env_vars_to_build: bool | None = None,
        source_type: VersionSourceType | None = None,
        source_files: list[dict[str, Any]] | None = None,
        git_repo_url: str | None = None,
        tarball_url: str | None = None,
        github_gist_url: str | None = None,
        timeout: Timeout = 'long',
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
            timeout: Timeout for the API HTTP request.

        Returns:
            The updated Actor version.
        """
        version_fields = CreateOrUpdateVersionRequest(
            build_tag=build_tag,
            env_vars=[EnvVar.model_validate(v) for v in env_vars] if env_vars else None,
            apply_env_vars_to_build=apply_env_vars_to_build,
            source_type=source_type,
            source_files=_source_file_list_adapter.validate_python(source_files) if source_files else None,
            git_repo_url=git_repo_url,
            tarball_url=tarball_url,
            github_gist_url=github_gist_url,
        )
        result = await self._update(timeout=timeout, **version_fields.model_dump(by_alias=True, exclude_none=True))
        return VersionResponse.model_validate(result).data

    async def delete(self, *, timeout: Timeout = 'long') -> None:
        """Delete the Actor version.

        https://docs.apify.com/api/v2#/reference/actors/version-object/delete-version

        Args:
            timeout: Timeout for the API HTTP request.
        """
        await self._delete(timeout=timeout)

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
