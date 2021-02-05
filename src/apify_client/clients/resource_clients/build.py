from typing import Any, Dict, Optional

from ..base.actor_job_base_client import ActorJobBaseClient


class BuildClient(ActorJobBaseClient):
    """Sub-client for manipulating a single actor build."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the BuildClient."""
        super().__init__(*args, resource_path='actor-builds', **kwargs)

    def get(self) -> Optional[Dict]:
        """Return information about the actor build.

        https://docs.apify.com/api/v2#/reference/actor-builds/build-object/get-build

        Returns:
            The retrieved actor build data
        """
        return self._get()

    def abort(self) -> Dict:
        """Abort the actor build which is starting or currently running and return its details.

        https://docs.apify.com/api/v2#/reference/actor-builds/abort-build/abort-build

        Returns:
            The data of the aborted actor build
        """
        return self._abort()

    def wait_for_finish(self, *, wait_secs: Optional[int] = None) -> Optional[Dict]:
        """Wait synchronously until the build finishes or the server times out.

        Args:
            wait_secs (Optional[int]): how long does the client wait for build to finish. None for indefinite.

        Returns:
            The actor build data. If the status on the object is not one of the terminal statuses (SUCEEDED, FAILED, TIMED_OUT, ABORTED)
            then the build has not yet finished.
        """
        return self._wait_for_finish(wait_secs=wait_secs)