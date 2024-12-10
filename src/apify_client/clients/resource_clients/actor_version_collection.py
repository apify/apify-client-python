from __future__ import annotations

from typing import TYPE_CHECKING, Any

from apify_shared.utils import filter_out_none_values_recursively, ignore_docs

from apify_client.clients.base import ResourceCollectionClient, ResourceCollectionClientAsync
from apify_client.clients.resource_clients.actor_version import _get_actor_version_representation

if TYPE_CHECKING:
    from apify_shared.consts import ActorSourceType
    from apify_shared.models import ListPage


class ActorVersionCollectionClient(ResourceCollectionClient):
    """Sub-client for manipulating Actor versions."""

    @ignore_docs
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'versions')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def list(self) -> ListPage[dict]:
        """List the available Actor versions.

        https://docs.apify.com/api/v2#/reference/actors/version-collection/get-list-of-versions

        Returns:
            The list of available Actor versions.
        """
        return self._list()

    def create(
        self,
        *,
        version_number: str,
        build_tag: str | None = None,
        env_vars: list[dict] | None = None,  # type: ignore[valid-type]
        apply_env_vars_to_build: bool | None = None,
        source_type: ActorSourceType,
        source_files: list[dict] | None = None,  # type: ignore[valid-type]
        git_repo_url: str | None = None,
        tarball_url: str | None = None,
        github_gist_url: str | None = None,
    ) -> dict:
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
                when `source_type` is `ActorSourceType.SOURCE_FILES`. See the API docs for the exact structure.
            git_repo_url: The URL of a Git repository from which the source code will be cloned.
                Required when `source_type` is `ActorSourceType.GIT_REPO`.
            tarball_url: The URL of a tarball or a zip archive from which the source code will be downloaded.
                Required when `source_type` is `ActorSourceType.TARBALL`.
            github_gist_url: The URL of a GitHub Gist from which the source will be downloaded.
                Required when `source_type` is `ActorSourceType.GITHUB_GIST`.

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

        return self._create(filter_out_none_values_recursively(actor_version_representation))


class ActorVersionCollectionClientAsync(ResourceCollectionClientAsync):
    """Async sub-client for manipulating Actor versions."""

    @ignore_docs
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'versions')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def list(self) -> ListPage[dict]:
        """List the available Actor versions.

        https://docs.apify.com/api/v2#/reference/actors/version-collection/get-list-of-versions

        Returns:
            The list of available Actor versions.
        """
        return await self._list()

    async def create(
        self,
        *,
        version_number: str,
        build_tag: str | None = None,
        env_vars: list[dict] | None = None,  # type: ignore[valid-type]
        apply_env_vars_to_build: bool | None = None,
        source_type: ActorSourceType,
        source_files: list[dict] | None = None,  # type: ignore[valid-type]
        git_repo_url: str | None = None,
        tarball_url: str | None = None,
        github_gist_url: str | None = None,
    ) -> dict:
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
                when `source_type` is `ActorSourceType.SOURCE_FILES`. See the API docs for the exact structure.
            git_repo_url: The URL of a Git repository from which the source code will be cloned.
                Required when `source_type` is `ActorSourceType.GIT_REPO`.
            tarball_url: The URL of a tarball or a zip archive from which the source code will be downloaded.
                Required when `source_type` is `ActorSourceType.TARBALL`.
            github_gist_url: The URL of a GitHub Gist from which the source will be downloaded.
                Required when `source_type` is `ActorSourceType.GITHUB_GIST`.

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

        return await self._create(filter_out_none_values_recursively(actor_version_representation))
