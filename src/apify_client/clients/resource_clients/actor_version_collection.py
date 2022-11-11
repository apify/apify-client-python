from typing import Any, Dict, List, Optional

from ..._utils import ListPage, _filter_out_none_values_recursively, _make_async_docs
from ...consts import ActorSourceType
from ..base import ResourceCollectionClient, ResourceCollectionClientAsync
from .actor_version import _get_actor_version_representation


class ActorVersionCollectionClient(ResourceCollectionClient):
    """Sub-client for manipulating actor versions."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the ActorVersionCollectionClient with the passed arguments."""
        resource_path = kwargs.pop('resource_path', 'versions')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def list(self) -> ListPage:
        """List the available actor versions.

        https://docs.apify.com/api/v2#/reference/actors/version-collection/get-list-of-versions

        Returns:
            ListPage: The list of available actor versions.
        """
        return self._list()

    def create(
        self,
        *,
        version_number: str,
        build_tag: Optional[str] = None,
        env_vars: Optional[List[Dict]] = None,
        apply_env_vars_to_build: Optional[bool] = None,
        source_type: ActorSourceType,
        source_files: Optional[List[Dict]] = None,
        git_repo_url: Optional[str] = None,
        tarball_url: Optional[str] = None,
        github_gist_url: Optional[str] = None,
    ) -> Dict:
        """Create a new actor version.

        https://docs.apify.com/api/v2#/reference/actors/version-collection/create-version

        Args:
            version_number (str): Major and minor version of the actor (e.g. ``1.0``)
            build_tag (str, optional): Tag that is automatically set to the latest successful build of the current version.
            env_vars (list of dict, optional): Environment variables that will be available to the actor run process,
                and optionally also to the build process. See the API docs for their exact structure.
            apply_env_vars_to_build (bool, optional): Whether the environment variables specified for the actor run
                will also be set to the actor build process.
            source_type (ActorSourceType): What source type is the actor version using.
            source_files (list of dict, optional): Source code comprised of multiple files, each an item of the array.
                Required when ``source_type`` is ``ActorSourceType.SOURCE_FILES``. See the API docs for the exact structure.
            git_repo_url (str, optional): The URL of a Git repository from which the source code will be cloned.
                Required when ``source_type`` is ``ActorSourceType.GIT_REPO``.
            tarball_url (str, optional): The URL of a tarball or a zip archive from which the source code will be downloaded.
                Required when ``source_type`` is ``ActorSourceType.TARBALL``.
            github_gist_url (str, optional): The URL of a GitHub Gist from which the source will be downloaded.
                Required when ``source_type`` is ``ActorSourceType.GITHUB_GIST``.

        Returns:
            dict: The created actor version
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

        return self._create(_filter_out_none_values_recursively(actor_version_representation))


class ActorVersionCollectionClientAsync(ResourceCollectionClientAsync):
    """Async sub-client for manipulating actor versions."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the ActorVersionCollectionClientAsync with the passed arguments."""
        resource_path = kwargs.pop('resource_path', 'versions')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    @_make_async_docs(src=ActorVersionCollectionClient.list)
    async def list(self) -> ListPage:
        return await self._list()

    @_make_async_docs(src=ActorVersionCollectionClient.create)
    async def create(
        self,
        *,
        version_number: str,
        build_tag: Optional[str] = None,
        env_vars: Optional[List[Dict]] = None,
        apply_env_vars_to_build: Optional[bool] = None,
        source_type: ActorSourceType,
        source_files: Optional[List[Dict]] = None,
        git_repo_url: Optional[str] = None,
        tarball_url: Optional[str] = None,
        github_gist_url: Optional[str] = None,
    ) -> Dict:
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

        return await self._create(_filter_out_none_values_recursively(actor_version_representation))
