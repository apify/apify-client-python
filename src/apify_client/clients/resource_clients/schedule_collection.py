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
    ) -> Dict:
        """Create a new schedule.

        https://docs.apify.com/api/v2#/reference/schedules/schedules-collection/create-schedule

        Args:
            cron_expression: The cron expression used by this schedule
            is_enabled: True if the schedule should be enabled
            is_exclusive: True if the schedule is exclusive
            name: The name of the schedule to create.
            actions: Actors or tasks that should be run on this schedule. See the API documentation for exact structure.

        Returns:
            The created schedule.
        """
        return self._create({
            "name": name,
            "isEnabled": is_enabled,
            "isExclusive": is_exclusive,
            "cronExpression": cron_expression,
            "actions": actions,
        })
