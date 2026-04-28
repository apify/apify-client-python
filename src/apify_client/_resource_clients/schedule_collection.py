from __future__ import annotations

from typing import TYPE_CHECKING, Any

from apify_client._docs import docs_group
from apify_client._iterable_list_page import (
    _LazyTask,
    build_iterable_list_page,
    build_iterable_list_page_async,
)
from apify_client._models_generated import (
    ListOfSchedulesResponse,
    Schedule,
    ScheduleCreate,
    ScheduleResponse,
)
from apify_client._pagination_classes import (
    ListPageOfSchedules,
    ListPageOfSchedulesAsync,
    PaginatedPage,
)
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync

if TYPE_CHECKING:
    from apify_client._models_generated import ScheduleShort
    from apify_client._types import Timeout


@docs_group('Resource clients')
class ScheduleCollectionClient(ResourceClient):
    """Sub-client for the schedule collection.

    Provides methods to manage the schedule collection, e.g. list or create schedules. Obtain an instance via an
    appropriate method on the `ApifyClient` class.
    """

    def __init__(
        self,
        *,
        resource_path: str = 'schedules',
        **kwargs: Any,
    ) -> None:
        super().__init__(
            resource_path=resource_path,
            **kwargs,
        )

    def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
        timeout: Timeout = 'medium',
    ) -> ListPageOfSchedules:
        """List the available schedules.

        The returned page also supports iteration: `for item in client.list(...)` yields individual
        schedules and transparently fetches further pages from the API.

        https://docs.apify.com/api/v2#/reference/schedules/schedules-collection/get-list-of-schedules

        Args:
            limit: How many schedules to retrieve.
            offset: What schedules to include as first when retrieving the list.
            desc: Whether to sort the schedules in descending order based on their modification date.
            timeout: Timeout for the API HTTP request.

        Returns:
            The list of available schedules matching the specified filters.
        """

        def _callback(**kwargs: Any) -> PaginatedPage[ScheduleShort]:
            result = self._list(timeout=timeout, **kwargs)
            data = ListOfSchedulesResponse.model_validate(result).data
            return PaginatedPage(
                items=data.items,
                count=data.count,
                limit=data.limit,
                total=data.total,
                offset=data.offset,
                desc=data.desc,
            )

        first_page = _callback(limit=limit, offset=offset, desc=desc)
        get_iterator = build_iterable_list_page(_callback, first_page, limit=limit, offset=offset, desc=desc)

        return ListPageOfSchedules(
            _get_iterator=get_iterator,
            items=first_page.items,
            count=first_page.count,
            limit=first_page.limit,
            total=first_page.total,
            offset=first_page.offset,
            desc=first_page.desc,
        )

    def create(
        self,
        *,
        cron_expression: str,
        is_enabled: bool,
        is_exclusive: bool,
        name: str | None = None,
        actions: list[dict[str, Any]] | None = None,  # ty: ignore[invalid-type-form]
        description: str | None = None,
        timezone: str | None = None,
        title: str | None = None,
        timeout: Timeout = 'short',
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
            timeout: Timeout for the API HTTP request.

        Returns:
            The created schedule.
        """
        if not actions:
            actions = []

        schedule_fields = ScheduleCreate(
            cron_expression=cron_expression,
            is_enabled=is_enabled,
            is_exclusive=is_exclusive,
            name=name,
            actions=actions or None,
            description=description,
            timezone=timezone,
            title=title,
        )
        result = self._create(timeout=timeout, **schedule_fields.model_dump(by_alias=True, exclude_none=True))
        return ScheduleResponse.model_validate(result).data


@docs_group('Resource clients')
class ScheduleCollectionClientAsync(ResourceClientAsync):
    """Sub-client for the schedule collection.

    Provides methods to manage the schedule collection, e.g. list or create schedules. Obtain an instance via an
    appropriate method on the `ApifyClientAsync` class.
    """

    def __init__(
        self,
        *,
        resource_path: str = 'schedules',
        **kwargs: Any,
    ) -> None:
        super().__init__(
            resource_path=resource_path,
            **kwargs,
        )

    def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        desc: bool | None = None,
        timeout: Timeout = 'medium',
    ) -> ListPageOfSchedulesAsync:
        """List the available schedules.

        The returned page also supports iteration: `async for item in client.list(...)` yields individual
        schedules and transparently fetches further pages from the API.

        https://docs.apify.com/api/v2#/reference/schedules/schedules-collection/get-list-of-schedules

        Args:
            limit: How many schedules to retrieve.
            offset: What schedules to include as first when retrieving the list.
            desc: Whether to sort the schedules in descending order based on their modification date.
            timeout: Timeout for the API HTTP request.

        Returns:
            The list of available schedules matching the specified filters.
        """

        async def _callback(**kwargs: Any) -> PaginatedPage[ScheduleShort]:
            result = await self._list(timeout=timeout, **kwargs)
            data = ListOfSchedulesResponse.model_validate(result).data
            return PaginatedPage(
                items=data.items,
                count=data.count,
                limit=data.limit,
                total=data.total,
                offset=data.offset,
                desc=data.desc,
            )

        fetch_first_page = _LazyTask(_callback(limit=limit, offset=offset, desc=desc))
        get_async_iterator = build_iterable_list_page_async(
            _callback, fetch_first_page, limit=limit, offset=offset, desc=desc
        )

        return ListPageOfSchedulesAsync(
            _awaitable_first_page=fetch_first_page,
            _get_async_iterator=get_async_iterator,
        )

    async def create(
        self,
        *,
        cron_expression: str,
        is_enabled: bool,
        is_exclusive: bool,
        name: str | None = None,
        actions: list[dict[str, Any]] | None = None,  # ty: ignore[invalid-type-form]
        description: str | None = None,
        timezone: str | None = None,
        title: str | None = None,
        timeout: Timeout = 'short',
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
            timeout: Timeout for the API HTTP request.

        Returns:
            The created schedule.
        """
        if not actions:
            actions = []

        schedule_fields = ScheduleCreate(
            cron_expression=cron_expression,
            is_enabled=is_enabled,
            is_exclusive=is_exclusive,
            name=name,
            actions=actions or None,
            description=description,
            timezone=timezone,
            title=title,
        )
        result = await self._create(timeout=timeout, **schedule_fields.model_dump(by_alias=True, exclude_none=True))
        return ScheduleResponse.model_validate(result).data
