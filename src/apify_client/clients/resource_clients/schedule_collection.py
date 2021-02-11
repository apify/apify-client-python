from typing import Any, Dict, List, Optional

from ..base.resource_collection_client import ResourceCollectionClient


class ScheduleCollectionClient(ResourceCollectionClient):
    """Sub-client for manipulating schedules."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the ScheduleCollectionClient with the passed arguments."""
        super().__init__(*args, resource_path='schedules', **kwargs)

    def list(self, *, limit: Optional[int] = None, offset: Optional[int] = None, desc: Optional[bool] = None) -> Dict:
        """List the available schedules.

        https://docs.apify.com/api/v2#/reference/schedules/schedules-collection/get-list-of-schedules

        Args:
            limit: How many schedules to retrieve
            offset: What schedules to include as first when retrieving the list
            desc: Whether to sort the schedules in descending order based on their modification date

        Returns:
            The list of available schedules matching the specified filters.
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
            The created schedule.
        """
        return self._create({
            "name": name,
            "isEnabled": is_enabled,
            "isExclusive": is_exclusive,
            "cronExpression": cron_expression,
            "actions": actions,
            "description": description,
            "timezone": timezone,
        })
