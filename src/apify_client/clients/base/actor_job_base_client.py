from .resource_client import ResourceClient

# from ..._utils import _parse_date_fields, _pluck_data


class ActorJobBaseClient(ResourceClient):
    """Base sub-client class for actor runs and actor builds."""
    def _wait_for_finish(self, wait_secs: int = None) -> None:
        # TODO implement when implementing run and build endpoints
        pass
