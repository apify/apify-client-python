from __future__ import annotations

from typing import Any

from apify_client._models import Schedule, ScheduleInvoked, ScheduleLogResponse, ScheduleResponse
from apify_client._representations import get_schedule_repr
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync
from apify_client._utils import catch_not_found_or_throw, filter_none_values, response_to_dict
from apify_client.errors import ApifyApiError


class ScheduleClient(ResourceClient):
    """Sub-client for manipulating a single schedule."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'schedules')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def get(self) -> Schedule | None:
        """Return information about the schedule.

        https://docs.apify.com/api/v2#/reference/schedules/schedule-object/get-schedule

        Returns:
            The retrieved schedule.
        """
        result = self._get()
        if result is None:
            return None
        return ScheduleResponse.model_validate(result).data

    def update(
        self,
        *,
        cron_expression: str | None = None,
        is_enabled: bool | None = None,
        is_exclusive: bool | None = None,
        name: str | None = None,
        actions: list[dict] | None = None,
        description: str | None = None,
        timezone: str | None = None,
        title: str | None = None,
    ) -> Schedule:
        """Update the schedule with specified fields.

        https://docs.apify.com/api/v2#/reference/schedules/schedule-object/update-schedule

        Args:
            cron_expression: The cron expression used by this schedule.
            is_enabled: True if the schedule should be enabled.
            is_exclusive: When set to true, don't start Actor or Actor task if it's still running from the previous
                schedule.
            name: The name of the schedule to create.
            actions: Actors or tasks that should be run on this schedule. See the API documentation for exact structure.
            description: Description of this schedule.
            timezone: Timezone in which your cron expression runs (TZ database name from
                https://en.wikipedia.org/wiki/List_of_tz_database_time_zones).
            title: A human-friendly equivalent of the name.

        Returns:
            The updated schedule.
        """
        schedule_representation = get_schedule_repr(
            cron_expression=cron_expression,
            is_enabled=is_enabled,
            is_exclusive=is_exclusive,
            name=name,
            actions=actions,
            description=description,
            timezone=timezone,
            title=title,
        )
        cleaned = filter_none_values(data=schedule_representation)

        result = self._update(updated_fields=cleaned)
        return ScheduleResponse.model_validate(result).data

    def delete(self) -> None:
        """Delete the schedule.

        https://docs.apify.com/api/v2#/reference/schedules/schedule-object/delete-schedule
        """
        self._delete()

    def get_log(self) -> list[ScheduleInvoked] | None:
        """Return log for the given schedule.

        https://docs.apify.com/api/v2#/reference/schedules/schedule-log/get-schedule-log

        Returns:
            Retrieved log of the given schedule.
        """
        try:
            response = self._http_client.call(
                url=self._build_url(path='log'),
                method='GET',
                params=self._build_params(),
            )
            result = response_to_dict(response=response)
            return ScheduleLogResponse.model_validate(result).data
        except ApifyApiError as exc:
            catch_not_found_or_throw(exc=exc)

        return None


class ScheduleClientAsync(ResourceClientAsync):
    """Async sub-client for manipulating a single schedule."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'schedules')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def get(self) -> Schedule | None:
        """Return information about the schedule.

        https://docs.apify.com/api/v2#/reference/schedules/schedule-object/get-schedule

        Returns:
            The retrieved schedule.
        """
        result = await self._get()
        if result is None:
            return None
        return ScheduleResponse.model_validate(result).data

    async def update(
        self,
        *,
        cron_expression: str | None = None,
        is_enabled: bool | None = None,
        is_exclusive: bool | None = None,
        name: str | None = None,
        actions: list[dict] | None = None,
        description: str | None = None,
        timezone: str | None = None,
        title: str | None = None,
    ) -> Schedule:
        """Update the schedule with specified fields.

        https://docs.apify.com/api/v2#/reference/schedules/schedule-object/update-schedule

        Args:
            cron_expression: The cron expression used by this schedule.
            is_enabled: True if the schedule should be enabled.
            is_exclusive: When set to true, don't start Actor or Actor task if it's still running from the previous
                schedule.
            name: The name of the schedule to create.
            actions: Actors or tasks that should be run on this schedule. See the API documentation for exact structure.
            description: Description of this schedule.
            timezone: Timezone in which your cron expression runs (TZ database name from
                https://en.wikipedia.org/wiki/List_of_tz_database_time_zones).
            title: A human-friendly equivalent of the name.

        Returns:
            The updated schedule.
        """
        schedule_representation = get_schedule_repr(
            cron_expression=cron_expression,
            is_enabled=is_enabled,
            is_exclusive=is_exclusive,
            name=name,
            actions=actions,
            description=description,
            timezone=timezone,
            title=title,
        )
        cleaned = filter_none_values(data=schedule_representation)

        result = await self._update(updated_fields=cleaned)
        return ScheduleResponse.model_validate(result).data

    async def delete(self) -> None:
        """Delete the schedule.

        https://docs.apify.com/api/v2#/reference/schedules/schedule-object/delete-schedule
        """
        await self._delete()

    async def get_log(self) -> list[ScheduleInvoked] | None:
        """Return log for the given schedule.

        https://docs.apify.com/api/v2#/reference/schedules/schedule-log/get-schedule-log

        Returns:
            Retrieved log of the given schedule.
        """
        try:
            response = await self._http_client.call(
                url=self._build_url(path='log'),
                method='GET',
                params=self._build_params(),
            )
            result = response_to_dict(response=response)
            return ScheduleLogResponse.model_validate(result).data
        except ApifyApiError as exc:
            catch_not_found_or_throw(exc=exc)

        return None
