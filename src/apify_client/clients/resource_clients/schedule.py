from typing import Any, Dict, List, Optional

from ..._errors import ApifyApiError
from ..._utils import _catch_not_found_or_throw, _parse_date_fields, _pluck_data
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

    def update(self, new_fields: Dict) -> Optional[Dict]:
        """Update the schedule with specified fields.

        https://docs.apify.com/api/v2#/reference/schedules/schedule-object/update-schedule

        Args:
            new_fields (dict): The fields of the schedule to update

        Returns:
            The updated schedule
        """
        return self._update(new_fields)

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
            return _parse_date_fields(_pluck_data(response.json()))
        except ApifyApiError as exc:
            _catch_not_found_or_throw(exc)

        return None
