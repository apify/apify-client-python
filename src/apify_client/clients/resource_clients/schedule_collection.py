from typing import Any, Dict, List, Optional

from ..._utils import ListPage, _filter_out_none_values_recursively, ignore_docs
from ..base import ResourceCollectionClient, ResourceCollectionClientAsync
from .schedule import _get_schedule_representation


class ScheduleCollectionClient(ResourceCollectionClient):
    """Sub-client for manipulating schedules."""

    @ignore_docs
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
    ) -> ListPage[Dict]:
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
        actions: Optional[List[Dict]] = None,
        description: Optional[str] = None,
        timezone: Optional[str] = None,
        title: Optional[str] = None,
    ) -> Dict:
        """Create a new schedule.

        https://docs.apify.com/api/v2#/reference/schedules/schedules-collection/create-schedule

        Args:
            cron_expression (str): The cron expression used by this schedule
            is_enabled (bool): True if the schedule should be enabled
            is_exclusive (bool): When set to true, don't start actor or actor task if it's still running from the previous schedule.
            name (str, optional): The name of the schedule to create.
            actions (list of dict, optional): Actors or tasks that should be run on this schedule. See the API documentation for exact structure.
            description (str, optional): Description of this schedule
            timezone (str, optional): Timezone in which your cron expression runs
                (TZ database name from https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)

        Returns:
            dict: The created schedule.
        """
        if not actions:
            actions = []

        schedule_representation = _get_schedule_representation(
            cron_expression=cron_expression,
            is_enabled=is_enabled,
            is_exclusive=is_exclusive,
            name=name,
            actions=actions,
            description=description,
            timezone=timezone,
            title=title,
        )

        return self._create(_filter_out_none_values_recursively(schedule_representation))


class ScheduleCollectionClientAsync(ResourceCollectionClientAsync):
    """Async sub-client for manipulating schedules."""

    @ignore_docs
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the ScheduleCollectionClientAsync with the passed arguments."""
        resource_path = kwargs.pop('resource_path', 'schedules')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def list(
        self,
        *,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        desc: Optional[bool] = None,
    ) -> ListPage[Dict]:
        """List the available schedules.

        https://docs.apify.com/api/v2#/reference/schedules/schedules-collection/get-list-of-schedules

        Args:
            limit (int, optional): How many schedules to retrieve
            offset (int, optional): What schedules to include as first when retrieving the list
            desc (bool, optional): Whether to sort the schedules in descending order based on their modification date

        Returns:
            ListPage: The list of available schedules matching the specified filters.
        """
        return await self._list(limit=limit, offset=offset, desc=desc)

    async def create(
        self,
        *,
        cron_expression: str,
        is_enabled: bool,
        is_exclusive: bool,
        name: Optional[str] = None,
        actions: Optional[List[Dict]] = None,
        description: Optional[str] = None,
        timezone: Optional[str] = None,
        title: Optional[str] = None,
    ) -> Dict:
        """Create a new schedule.

        https://docs.apify.com/api/v2#/reference/schedules/schedules-collection/create-schedule

        Args:
            cron_expression (str): The cron expression used by this schedule
            is_enabled (bool): True if the schedule should be enabled
            is_exclusive (bool): When set to true, don't start actor or actor task if it's still running from the previous schedule.
            name (str, optional): The name of the schedule to create.
            actions (list of dict, optional): Actors or tasks that should be run on this schedule. See the API documentation for exact structure.
            description (str, optional): Description of this schedule
            timezone (str, optional): Timezone in which your cron expression runs
                (TZ database name from https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)

        Returns:
            dict: The created schedule.
        """
        if not actions:
            actions = []

        schedule_representation = _get_schedule_representation(
            cron_expression=cron_expression,
            is_enabled=is_enabled,
            is_exclusive=is_exclusive,
            name=name,
            actions=actions,
            description=description,
            timezone=timezone,
            title=title,
        )

        return await self._create(_filter_out_none_values_recursively(schedule_representation))
