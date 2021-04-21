from typing import Any, Dict, List, Optional

from ..._utils import ListPage, _snake_case_to_camel_case
from ..base import ResourceCollectionClient


class ScheduleCollectionClient(ResourceCollectionClient):
    """Sub-client for manipulating schedules."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the ScheduleCollectionClient with the passed arguments."""
        resource_path = kwargs.pop('resource_path', 'schedules')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def list(
        self,
        *,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        desc: Optional[bool] = None,
    ) -> ListPage:
        """List the available schedules.

        https://docs.apify.com/api/v2#/reference/schedules/schedules-collection/get-list-of-schedules

        Args:
            limit (int, optional): How many schedules to retrieve
            offset (int, optional): What schedules to include as first when retrieving the list
            desc (bool, optional): Whether to sort the schedules in descending order based on their modification date

        Returns:
            ListPage: The list of available schedules matching the specified filters.
        """
        return self._list(limit=limit, offset=offset, desc=desc)

    def create(
        self,
        *,
        cron_expression: str,
        is_enabled: bool,
        is_exclusive: bool,
        name: Optional[str] = None,
        actions: List[Dict] = [],
        description: Optional[str] = None,
        timezone: Optional[str] = None,
    ) -> Dict:
        """Create a new schedule.

        https://docs.apify.com/api/v2#/reference/schedules/schedules-collection/create-schedule

        Args:
            cron_expression: The cron expression used by this schedule
            is_enabled: True if the schedule should be enabled
            is_exclusive: When set to true, don't start actor or actor task if it's still running from the previous schedule.
            name: The name of the schedule to create.
            actions: Actors or tasks that should be run on this schedule. See the API documentation for exact structure.
            description: Description of this schedule
            timezone: Timezone in which your cron expression runs (TZ database name from https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)

        Returns:
            dict: The created schedule.
        """
        kwargs = {
            _snake_case_to_camel_case(key): value
            for key, value in locals().items() if key != 'self' and value is not None
        }
        return self._create(kwargs)
