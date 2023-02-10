from typing import Any, Dict, List, Optional

from ..._errors import ApifyApiError
from ..._utils import _catch_not_found_or_throw, _filter_out_none_values_recursively, _pluck_data_as_list, ignore_docs
from ..base import ResourceClient, ResourceClientAsync


def _get_schedule_representation(
    cron_expression: Optional[str] = None,
    is_enabled: Optional[bool] = None,
    is_exclusive: Optional[bool] = None,
    name: Optional[str] = None,
    actions: Optional[List[Dict]] = None,
    description: Optional[str] = None,
    timezone: Optional[str] = None,
    title: Optional[str] = None,
) -> Dict:
    return {
        'cronExpression': cron_expression,
        'isEnabled': is_enabled,
        'isExclusive': is_exclusive,
        'name': name,
        'actions': actions,
        'description': description,
        'timezone': timezone,
        'title': title,
    }


class ScheduleClient(ResourceClient):
    """Sub-client for manipulating a single schedule."""

    @ignore_docs
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the ScheduleClient."""
        resource_path = kwargs.pop('resource_path', 'schedules')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def get(self) -> Optional[Dict]:
        """Return information about the schedule.

        https://docs.apify.com/api/v2#/reference/schedules/schedule-object/get-schedule

        Returns:
            dict, optional: The retrieved schedule
        """
        return self._get()

    def update(
        self,
        *,
        cron_expression: Optional[str] = None,
        is_enabled: Optional[bool] = None,
        is_exclusive: Optional[bool] = None,
        name: Optional[str] = None,
        actions: Optional[List[Dict]] = None,
        description: Optional[str] = None,
        timezone: Optional[str] = None,
        title: Optional[str] = None,
    ) -> Dict:
        """Update the schedule with specified fields.

        https://docs.apify.com/api/v2#/reference/schedules/schedule-object/update-schedule

        Args:
            cron_expression (str, optional): The cron expression used by this schedule
            is_enabled (bool, optional): True if the schedule should be enabled
            is_exclusive (bool, optional): When set to true, don't start actor or actor task if it's still running from the previous schedule.
            name (str, optional): The name of the schedule to create.
            actions (list of dict, optional): Actors or tasks that should be run on this schedule. See the API documentation for exact structure.
            description (str, optional): Description of this schedule
            timezone (str, optional): Timezone in which your cron expression runs
                                      (TZ database name from https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)
            title (str, optional): A human-friendly equivalent of the name

        Returns:
            dict: The updated schedule
        """
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

        return self._update(_filter_out_none_values_recursively(schedule_representation))

    def delete(self) -> None:
        """Delete the schedule.

        https://docs.apify.com/api/v2#/reference/schedules/schedule-object/delete-schedule
        """
        self._delete()

    def get_log(self) -> Optional[List]:
        """Return log for the given schedule.

        https://docs.apify.com/api/v2#/reference/schedules/schedule-log/get-schedule-log

        Returns:
            list, optional: Retrieved log of the given schedule
        """
        try:
            response = self.http_client.call(
                url=self._url('log'),
                method='GET',
                params=self._params(),
            )
            return _pluck_data_as_list(response.json())
        except ApifyApiError as exc:
            _catch_not_found_or_throw(exc)

        return None


class ScheduleClientAsync(ResourceClientAsync):
    """Async sub-client for manipulating a single schedule."""

    @ignore_docs
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the ScheduleClientAsync."""
        resource_path = kwargs.pop('resource_path', 'schedules')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def get(self) -> Optional[Dict]:
        """Return information about the schedule.

        https://docs.apify.com/api/v2#/reference/schedules/schedule-object/get-schedule

        Returns:
            dict, optional: The retrieved schedule
        """
        return await self._get()

    async def update(
        self,
        *,
        cron_expression: Optional[str] = None,
        is_enabled: Optional[bool] = None,
        is_exclusive: Optional[bool] = None,
        name: Optional[str] = None,
        actions: Optional[List[Dict]] = None,
        description: Optional[str] = None,
        timezone: Optional[str] = None,
        title: Optional[str] = None,
    ) -> Dict:
        """Update the schedule with specified fields.

        https://docs.apify.com/api/v2#/reference/schedules/schedule-object/update-schedule

        Args:
            cron_expression (str, optional): The cron expression used by this schedule
            is_enabled (bool, optional): True if the schedule should be enabled
            is_exclusive (bool, optional): When set to true, don't start actor or actor task if it's still running from the previous schedule.
            name (str, optional): The name of the schedule to create.
            actions (list of dict, optional): Actors or tasks that should be run on this schedule. See the API documentation for exact structure.
            description (str, optional): Description of this schedule
            timezone (str, optional): Timezone in which your cron expression runs
                                      (TZ database name from https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)
            title (str, optional): A human-friendly equivalent of the name

        Returns:
            dict: The updated schedule
        """
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

        return await self._update(_filter_out_none_values_recursively(schedule_representation))

    async def delete(self) -> None:
        """Delete the schedule.

        https://docs.apify.com/api/v2#/reference/schedules/schedule-object/delete-schedule
        """
        await self._delete()

    async def get_log(self) -> Optional[List]:
        """Return log for the given schedule.

        https://docs.apify.com/api/v2#/reference/schedules/schedule-log/get-schedule-log

        Returns:
            list, optional: Retrieved log of the given schedule
        """
        try:
            response = await self.http_client.call(
                url=self._url('log'),
                method='GET',
                params=self._params(),
            )
            return _pluck_data_as_list(response.json())
        except ApifyApiError as exc:
            _catch_not_found_or_throw(exc)

        return None
