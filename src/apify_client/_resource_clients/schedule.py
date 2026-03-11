from __future__ import annotations

from typing import TYPE_CHECKING, Any

from apify_client._docs import docs_group
from apify_client._models import (
    Schedule,
    ScheduleCreate,
    ScheduleCreateActions,
    ScheduleInvoked,
    ScheduleLogResponse,
    ScheduleResponse,
)
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync
from apify_client._utils import catch_not_found_or_throw, response_to_dict
from apify_client.errors import ApifyApiError

if TYPE_CHECKING:
    from apify_client._types import Timeout


@docs_group('Resource clients')
class ScheduleClient(ResourceClient):
    """Sub-client for managing a specific schedule.

    Provides methods to manage a specific schedule, e.g. get, update, or delete it. Obtain an instance via an
    appropriate method on the `ApifyClient` class.
    """

    def __init__(
        self,
        *,
        resource_id: str,
        resource_path: str = 'schedules',
        **kwargs: Any,
    ) -> None:
        super().__init__(
            resource_id=resource_id,
            resource_path=resource_path,
            **kwargs,
        )

    def get(self, *, timeout: Timeout = 'short') -> Schedule | None:
        """Return information about the schedule.

        https://docs.apify.com/api/v2#/reference/schedules/schedule-object/get-schedule

        Args:
            timeout: Timeout for the API HTTP request.

        Returns:
            The retrieved schedule.
        """
        result = self._get(timeout=timeout)
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
        actions: list[dict[str, Any]] | None = None,
        description: str | None = None,
        timezone: str | None = None,
        title: str | None = None,
        timeout: Timeout = 'short',
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
            timeout: Timeout for the API HTTP request.

        Returns:
            The updated schedule.
        """
        schedule_fields = ScheduleCreate(
            cron_expression=cron_expression,
            is_enabled=is_enabled,
            is_exclusive=is_exclusive,
            name=name,
            actions=[ScheduleCreateActions.model_validate(a) for a in actions] if actions else None,
            description=description,
            timezone=timezone,
            title=title,
        )
        result = self._update(timeout=timeout, **schedule_fields.model_dump(by_alias=True, exclude_none=True))
        return ScheduleResponse.model_validate(result).data

    def delete(self, *, timeout: Timeout = 'short') -> None:
        """Delete the schedule.

        https://docs.apify.com/api/v2#/reference/schedules/schedule-object/delete-schedule

        Args:
            timeout: Timeout for the API HTTP request.
        """
        self._delete(timeout=timeout)

    def get_log(self, *, timeout: Timeout = 'medium') -> list[ScheduleInvoked] | None:
        """Return log for the given schedule.

        https://docs.apify.com/api/v2#/reference/schedules/schedule-log/get-schedule-log

        Args:
            timeout: Timeout for the API HTTP request.

        Returns:
            Retrieved log of the given schedule.
        """
        try:
            response = self._http_client.call(
                url=self._build_url('log'),
                method='GET',
                params=self._build_params(),
                timeout=timeout,
            )
            result = response_to_dict(response)
            return ScheduleLogResponse.model_validate(result).data
        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

        return None


@docs_group('Resource clients')
class ScheduleClientAsync(ResourceClientAsync):
    """Sub-client for managing a specific schedule.

    Provides methods to manage a specific schedule, e.g. get, update, or delete it. Obtain an instance via an
    appropriate method on the `ApifyClientAsync` class.
    """

    def __init__(
        self,
        *,
        resource_id: str,
        resource_path: str = 'schedules',
        **kwargs: Any,
    ) -> None:
        super().__init__(
            resource_id=resource_id,
            resource_path=resource_path,
            **kwargs,
        )

    async def get(self, *, timeout: Timeout = 'short') -> Schedule | None:
        """Return information about the schedule.

        https://docs.apify.com/api/v2#/reference/schedules/schedule-object/get-schedule

        Args:
            timeout: Timeout for the API HTTP request.

        Returns:
            The retrieved schedule.
        """
        result = await self._get(timeout=timeout)
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
        actions: list[dict[str, Any]] | None = None,
        description: str | None = None,
        timezone: str | None = None,
        title: str | None = None,
        timeout: Timeout = 'short',
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
            timeout: Timeout for the API HTTP request.

        Returns:
            The updated schedule.
        """
        schedule_fields = ScheduleCreate(
            cron_expression=cron_expression,
            is_enabled=is_enabled,
            is_exclusive=is_exclusive,
            name=name,
            actions=[ScheduleCreateActions.model_validate(a) for a in actions] if actions else None,
            description=description,
            timezone=timezone,
            title=title,
        )
        result = await self._update(timeout=timeout, **schedule_fields.model_dump(by_alias=True, exclude_none=True))
        return ScheduleResponse.model_validate(result).data

    async def delete(self, *, timeout: Timeout = 'short') -> None:
        """Delete the schedule.

        https://docs.apify.com/api/v2#/reference/schedules/schedule-object/delete-schedule

        Args:
            timeout: Timeout for the API HTTP request.
        """
        await self._delete(timeout=timeout)

    async def get_log(self, *, timeout: Timeout = 'medium') -> list[ScheduleInvoked] | None:
        """Return log for the given schedule.

        https://docs.apify.com/api/v2#/reference/schedules/schedule-log/get-schedule-log

        Args:
            timeout: Timeout for the API HTTP request.

        Returns:
            Retrieved log of the given schedule.
        """
        try:
            response = await self._http_client.call(
                url=self._build_url('log'),
                method='GET',
                params=self._build_params(),
                timeout=timeout,
            )
            result = response_to_dict(response)
            return ScheduleLogResponse.model_validate(result).data
        except ApifyApiError as exc:
            catch_not_found_or_throw(exc)

        return None
