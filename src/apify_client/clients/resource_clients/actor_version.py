from typing import Any, Dict, List, Optional

from ..._utils import _filter_out_none_values_recursively, _maybe_extract_enum_member_value
from ...consts import ActorSourceType
from ..base import ResourceClient


def _get_actor_version_representation(
    *,
    version_number: Optional[str] = None,
    build_tag: Optional[str] = None,
    env_vars: Optional[List[Dict]] = None,
    apply_env_vars_to_build: Optional[bool] = None,
    source_type: Optional[ActorSourceType] = None,
    source_files: Optional[List[Dict]] = None,
    git_repo_url: Optional[str] = None,
    tarball_url: Optional[str] = None,
    github_gist_url: Optional[str] = None,
) -> Dict:
    return {
        'versionNumber': version_number,
        'buildTag': build_tag,
        'envVars': env_vars,
        'applyEnvVarsToBuild': apply_env_vars_to_build,
        'sourceType': _maybe_extract_enum_member_value(source_type),
        'sourceFiles': source_files,
        'gitRepoUrl': git_repo_url,
        'tarballUrl': tarball_url,
        'gitHubGistUrl': github_gist_url,
    }


class ActorVersionClient(ResourceClient):
    """Sub-client for manipulating a single actor version."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the ActorVersionClient."""
        resource_path = kwargs.pop('resource_path', 'versions')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def get(self) -> Optional[Dict]:
        """Return information about the actor version.

        https://docs.apify.com/api/v2#/reference/actors/version-object/get-version

        Returns:
            dict, optional: The retrieved actor version data
        """
        return self._get()

    def update(
        self,
        *,
        build_tag: Optional[str] = None,
        env_vars: Optional[List[Dict]] = None,
        apply_env_vars_to_build: Optional[bool] = None,
        source_type: Optional[ActorSourceType] = None,
        source_files: Optional[List[Dict]] = None,
        git_repo_url: Optional[str] = None,
        tarball_url: Optional[str] = None,
        github_gist_url: Optional[str] = None,
    ) -> Dict:
        """Update the actor version with specified fields.

        https://docs.apify.com/api/v2#/reference/actors/version-object/update-version

        Args:
            build_tag (str, optional): Tag that is automatically set to the latest successful build of the current version.
            env_vars (list of dict, optional): Environment variables that will be available to the actor run process,
                and optionally also to the build process. See the API docs for their exact structure.
            apply_env_vars_to_build (bool, optional): Whether the environment variables specified for the actor run
                will also be set to the actor build process.
            source_type (ActorSourceType, optional): What source type is the actor version using.
            source_files (list of dict, optional): Source code comprised of multiple files, each an item of the array.
                Required when ``source_type`` is ``ActorSourceType.SOURCE_FILES``. See the API docs for the exact structure.
            git_repo_url (str, optional): The URL of a Git repository from which the source code will be cloned.
                Required when ``source_type`` is ``ActorSourceType.GIT_REPO``.
            tarball_url (str, optional): The URL of a tarball or a zip archive from which the source code will be downloaded.
                Required when ``source_type`` is ``ActorSourceType.TARBALL``.
            github_gist_url (str, optional): The URL of a GitHub Gist from which the source will be downloaded.
                Required when ``source_type`` is ``ActorSourceType.GITHUB_GIST``.

        Returns:
            dict: The updated actor version
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

        return self._update(_filter_out_none_values_recursively(actor_version_representation))

    def delete(self) -> None:
        """Delete the actor version.

        https://docs.apify.com/api/v2#/reference/actors/version-object/delete-version
        """
        return self._delete()
