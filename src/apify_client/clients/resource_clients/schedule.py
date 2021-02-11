from typing import Any, Dict, List, Optional

from ..._errors import ApifyApiError
from ..._utils import _catch_not_found_or_throw, _pluck_data_as_list, _snake_case_to_camel_case
from ..base.resource_client import ResourceClient


class ScheduleClient(ResourceClient):
    """Sub-client for manipulating schedules."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the ScheduleClient."""
        super().__init__(*args, resource_path='schedules', **kwargs)

    def get(self) -> Optional[Dict]:
        """Return information about schedule.

        https://docs.apify.com/api/v2#/reference/schedules/schedule-object/get-schedule

        Returns:
            The retrieved schedule
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
    ) -> Optional[Dict]:
        """Update the schedule with specified fields.

        https://docs.apify.com/api/v2#/reference/schedules/schedule-object/update-schedule

        Args:
            cron_expression: The cron expression used by this schedule
            is_enabled: True if the schedule should be enabled
            is_exclusive: When set to true, don't start actor or actor task if it's still running from the previous schedule.
            name: The name of the schedule to create.
            actions: Actors or tasks that should be run on this schedule. See the API documentation for exact structure.
            description: Description of this schedule
            timezone: Timezone in which your cron expression runs (TZ database name from https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)

        Returns:
            The updated schedule
        """
        updated_kwargs = {
            _snake_case_to_camel_case(key): value
            for key, value in locals().items() if key != 'self' and value is not None
        }
        return self._update(updated_kwargs)

    def delete(self) -> None:
        """Delete the schedule.

        https://docs.apify.com/api/v2#/reference/schedules/schedule-object/delete-schedule
        """
        self._delete()

    def get_log(self) -> Optional[List]:
        """Return log for the given schedule.

        https://docs.apify.com/api/v2#/reference/schedules/schedule-log/get-schedule-log

        Returns:
            Retrieved log of the given schedule
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
