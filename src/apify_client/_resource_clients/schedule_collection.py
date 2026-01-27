from __future__ import annotations

from typing import Any

from apify_client._models import (
    GetListOfSchedulesResponse,
    GetScheduleResponse,
    ListOfSchedules,
    Schedule,
)
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync
from apify_client._resource_clients.schedule import _get_schedule_representation
from apify_client._utils import filter_none_values, response_to_dict


class ScheduleCollectionClient(ResourceClient):
    """Sub-client for manipulating schedules."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'schedules')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
    ) -> ListOfSchedules:
        """List the available schedules.

        https://docs.apify.com/api/v2#/reference/schedules/schedules-collection/get-list-of-schedules

        Args:
            limit: How many schedules to retrieve.
            offset: What schedules to include as first when retrieving the list.
            desc: Whether to sort the schedules in descending order based on their modification date.

        Returns:
            The list of available schedules matching the specified filters.
        """
        response = self.http_client.call(
            url=self._url(),
            method='GET',
            params=self._build_params(limit=limit, offset=offset, desc=desc),
        )
        response_as_dict = response_to_dict(response)
        return GetListOfSchedulesResponse.model_validate(response_as_dict).data

    def create(
        self,
        *,
        cron_expression: str,
        is_enabled: bool,
        is_exclusive: bool,
        name: str | None = None,
        actions: list[dict] | None = None,  # ty: ignore[invalid-type-form]
        description: str | None = None,
        timezone: str | None = None,
        title: str | None = None,
    ) -> Schedule:
        """Create a new schedule.

        https://docs.apify.com/api/v2#/reference/schedules/schedules-collection/create-schedule

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
            title: Title of this schedule.

        Returns:
            The created schedule.
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

        response = self.http_client.call(
            url=self._url(),
            method='POST',
            params=self._build_params(),
            json=filter_none_values(schedule_representation),
        )

        result = response_to_dict(response)
        return GetScheduleResponse.model_validate(result).data


class ScheduleCollectionClientAsync(ResourceClientAsync):
    """Async sub-client for manipulating schedules."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        resource_path = kwargs.pop('resource_path', 'schedules')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
    ) -> ListOfSchedules:
        """List the available schedules.

        https://docs.apify.com/api/v2#/reference/schedules/schedules-collection/get-list-of-schedules

        Args:
            limit: How many schedules to retrieve.
            offset: What schedules to include as first when retrieving the list.
            desc: Whether to sort the schedules in descending order based on their modification date.

        Returns:
            The list of available schedules matching the specified filters.
        """
        response = await self.http_client.call(
            url=self._url(),
            method='GET',
            params=self._build_params(limit=limit, offset=offset, desc=desc),
        )
        response_as_dict = response_to_dict(response)
        return GetListOfSchedulesResponse.model_validate(response_as_dict).data

    async def create(
        self,
        *,
        cron_expression: str,
        is_enabled: bool,
        is_exclusive: bool,
        name: str | None = None,
        actions: list[dict] | None = None,  # ty: ignore[invalid-type-form]
        description: str | None = None,
        timezone: str | None = None,
        title: str | None = None,
    ) -> Schedule:
        """Create a new schedule.

        https://docs.apify.com/api/v2#/reference/schedules/schedules-collection/create-schedule

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
            title: Title of this schedule.

        Returns:
            The created schedule.
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

        response = await self.http_client.call(
            url=self._url(),
            method='POST',
            params=self._build_params(),
            json=filter_none_values(schedule_representation),
        )

        result = response_to_dict(response)
        return GetScheduleResponse.model_validate(result).data
