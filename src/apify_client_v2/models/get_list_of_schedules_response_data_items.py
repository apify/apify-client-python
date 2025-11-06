from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
  from ..models.get_list_of_schedules_response_data_items_actions import GetListOfSchedulesResponseDataItemsActions





T = TypeVar("T", bound="GetListOfSchedulesResponseDataItems")



@_attrs_define
class GetListOfSchedulesResponseDataItems:
    """ 
        Attributes:
            id (str):  Example: asdLZtadYvn4mBZmm.
            user_id (str):  Example: wRsJZtadYvn4mBZmm.
            name (str):  Example: my-schedule.
            created_at (str):  Example: 2019-12-12T07:34:14.202Z.
            modified_at (str):  Example: 2019-12-20T06:33:11.202Z.
            last_run_at (str):  Example: 2019-04-12T07:33:10.202Z.
            next_run_at (str):  Example: 2019-04-12T07:34:10.202Z.
            is_enabled (bool):  Example: True.
            is_exclusive (bool):  Example: True.
            cron_expression (str):  Example: * * * * *.
            timezone (str):  Example: UTC.
            actions (list[GetListOfSchedulesResponseDataItemsActions]):
     """

    id: str
    user_id: str
    name: str
    created_at: str
    modified_at: str
    last_run_at: str
    next_run_at: str
    is_enabled: bool
    is_exclusive: bool
    cron_expression: str
    timezone: str
    actions: list[GetListOfSchedulesResponseDataItemsActions]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.get_list_of_schedules_response_data_items_actions import GetListOfSchedulesResponseDataItemsActions
        id = self.id

        user_id = self.user_id

        name = self.name

        created_at = self.created_at

        modified_at = self.modified_at

        last_run_at = self.last_run_at

        next_run_at = self.next_run_at

        is_enabled = self.is_enabled

        is_exclusive = self.is_exclusive

        cron_expression = self.cron_expression

        timezone = self.timezone

        actions = []
        for actions_item_data in self.actions:
            actions_item = actions_item_data.to_dict()
            actions.append(actions_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "userId": user_id,
            "name": name,
            "createdAt": created_at,
            "modifiedAt": modified_at,
            "lastRunAt": last_run_at,
            "nextRunAt": next_run_at,
            "isEnabled": is_enabled,
            "isExclusive": is_exclusive,
            "cronExpression": cron_expression,
            "timezone": timezone,
            "actions": actions,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_list_of_schedules_response_data_items_actions import GetListOfSchedulesResponseDataItemsActions
        d = dict(src_dict)
        id = d.pop("id")

        user_id = d.pop("userId")

        name = d.pop("name")

        created_at = d.pop("createdAt")

        modified_at = d.pop("modifiedAt")

        last_run_at = d.pop("lastRunAt")

        next_run_at = d.pop("nextRunAt")

        is_enabled = d.pop("isEnabled")

        is_exclusive = d.pop("isExclusive")

        cron_expression = d.pop("cronExpression")

        timezone = d.pop("timezone")

        actions = []
        _actions = d.pop("actions")
        for actions_item_data in (_actions):
            actions_item = GetListOfSchedulesResponseDataItemsActions.from_dict(actions_item_data)



            actions.append(actions_item)


        get_list_of_schedules_response_data_items = cls(
            id=id,
            user_id=user_id,
            name=name,
            created_at=created_at,
            modified_at=modified_at,
            last_run_at=last_run_at,
            next_run_at=next_run_at,
            is_enabled=is_enabled,
            is_exclusive=is_exclusive,
            cron_expression=cron_expression,
            timezone=timezone,
            actions=actions,
        )


        get_list_of_schedules_response_data_items.additional_properties = d
        return get_list_of_schedules_response_data_items

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
