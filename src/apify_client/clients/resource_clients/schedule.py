from __future__ import annotations

from typing import Any

from apify_shared.utils import filter_out_none_values_recursively, ignore_docs

from apify_client._errors import ApifyApiError
from apify_client._utils import catch_not_found_or_throw, pluck_data_as_list
from apify_client.clients.base import ResourceClient, ResourceClientAsync


def _get_schedule_representation(
    cron_expression: str | None = None,
    is_enabled: bool | None = None,
    is_exclusive: bool | None = None,
    name: str | None = None,
    actions: list[dict] | None = None,
    description: str | None = None,
    timezone: str | None = None,
    title: str | None = None,
) -> dict:
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
    def __init__(self: ScheduleClient, *args: Any, **kwargs: Any) -> None:
        """Initialize the ScheduleClient."""
        resource_path = kwargs.pop('resource_path', 'schedules')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def get(self: ScheduleClient) -> dict | None:
        """Return information about the schedule.

        https://docs.apify.com/api/v2#/reference/schedules/schedule-object/get-schedule

        Returns:
            dict, optional: The retrieved schedule
        """
        return self._get()

    def update(
        self: ScheduleClient,
        *,
        cron_expression: str | None = None,
        is_enabled: bool | None = None,
        is_exclusive: bool | None = None,
        name: str | None = None,
        actions: list[dict] | None = None,
        description: str | None = None,
        timezone: str | None = None,
        title: str | None = None,
    ) -> dict:
        """Update the schedule with specified fields.

        https://docs.apify.com/api/v2#/reference/schedules/schedule-object/update-schedule

        Args:
            cron_expression (str, optional): The cron expression used by this schedule
            is_enabled (bool, optional): True if the schedule should be enabled
            is_exclusive (bool, optional): When set to true, don't start Actor or Actor task if it's still running from the previous schedule.
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

        return self._update(filter_out_none_values_recursively(schedule_representation))

    def delete(self: ScheduleClient) -> None:
        """Delete the schedule.

        https://docs.apify.com/api/v2#/reference/schedules/schedule-object/delete-schedule
        """
        self._delete()

    def get_log(self: ScheduleClient) -> list | None:
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
            return pluck_data_as_list(response.json())
        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

        return None


class ScheduleClientAsync(ResourceClientAsync):
    """Async sub-client for manipulating a single schedule."""

    @ignore_docs
    def __init__(self: ScheduleClientAsync, *args: Any, **kwargs: Any) -> None:
        """Initialize the ScheduleClientAsync."""
        resource_path = kwargs.pop('resource_path', 'schedules')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def get(self: ScheduleClientAsync) -> dict | None:
        """Return information about the schedule.

        https://docs.apify.com/api/v2#/reference/schedules/schedule-object/get-schedule

        Returns:
            dict, optional: The retrieved schedule
        """
        return await self._get()

    async def update(
        self: ScheduleClientAsync,
        *,
        cron_expression: str | None = None,
        is_enabled: bool | None = None,
        is_exclusive: bool | None = None,
        name: str | None = None,
        actions: list[dict] | None = None,
        description: str | None = None,
        timezone: str | None = None,
        title: str | None = None,
    ) -> dict:
        """Update the schedule with specified fields.

        https://docs.apify.com/api/v2#/reference/schedules/schedule-object/update-schedule

        Args:
            cron_expression (str, optional): The cron expression used by this schedule
            is_enabled (bool, optional): True if the schedule should be enabled
            is_exclusive (bool, optional): When set to true, don't start Actor or Actor task if it's still running from the previous schedule.
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

        return await self._update(filter_out_none_values_recursively(schedule_representation))

    async def delete(self: ScheduleClientAsync) -> None:
        """Delete the schedule.

        https://docs.apify.com/api/v2#/reference/schedules/schedule-object/delete-schedule
        """
        await self._delete()

    async def get_log(self: ScheduleClientAsync) -> list | None:
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
            return pluck_data_as_list(response.json())
        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

        return None
