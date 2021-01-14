import math
from datetime import datetime
from typing import Dict, Optional

from ..._consts import TERMINAL_ACTOR_JOB_STATUSES, ActorJobStatus
from ..._utils import _parse_date_fields, _pluck_data
from .resource_client import ResourceClient


class ActorJobBaseClient(ResourceClient):
    """Base sub-client class for actor runs and actor builds."""

    def _wait_for_finish(self, wait_secs: Optional[int] = None) -> Dict:
        started_at = datetime.now()
        should_repeat = True
        job: Optional[Dict] = None
        seconds_elapsed = 0

        while(should_repeat):
            wait_for_finish = 9999
            if wait_secs is not None:
                wait_for_finish = wait_secs - seconds_elapsed

            response = self.http_client.call(
                url=self.url,
                method='GET',
                params=self._params(wait_for_finish=wait_for_finish),
            )
            job = _parse_date_fields(_pluck_data(response.json()))

            seconds_elapsed = math.floor(((datetime.now() - started_at).total_seconds()))
            if (
                ActorJobStatus(job['status']) in TERMINAL_ACTOR_JOB_STATUSES or (wait_secs is not None and seconds_elapsed >= wait_secs)
            ):
                should_repeat = False

        if job is None:
            raise ValueError(f"Waiting for actor job with ID {self.resource_id} failed.")

        return job
