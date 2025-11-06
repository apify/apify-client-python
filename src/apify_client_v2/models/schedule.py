from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.schedule_actions import ScheduleActions





T = TypeVar("T", bound="Schedule")



@_attrs_define
class Schedule:
    """ 
        Attributes:
            id (str):  Example: asdLZtadYvn4mBZmm.
            user_id (str):  Example: wRsJZtadYvn4mBZmm.
            name (str):  Example: my-schedule.
            cron_expression (str):  Example: * * * * *.
            timezone (str):  Example: UTC.
            is_enabled (bool):  Example: True.
            is_exclusive (bool):  Example: True.
            created_at (str):  Example: 2019-12-12T07:34:14.202Z.
            modified_at (str):  Example: 2019-12-20T06:33:11.202Z.
            actions (list[ScheduleActions]):
            description (None | str | Unset):  Example: Schedule of actor ....
            next_run_at (None | str | Unset):  Example: 2019-04-12T07:34:10.202Z.
            last_run_at (None | str | Unset):  Example: 2019-04-12T07:33:10.202Z.
     """

    id: str
    user_id: str
    name: str
    cron_expression: str
    timezone: str
    is_enabled: bool
    is_exclusive: bool
    created_at: str
    modified_at: str
    actions: list[ScheduleActions]
    description: None | str | Unset = UNSET
    next_run_at: None | str | Unset = UNSET
    last_run_at: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.schedule_actions import ScheduleActions
        id = self.id

        user_id = self.user_id

        name = self.name

        cron_expression = self.cron_expression

        timezone = self.timezone

        is_enabled = self.is_enabled

        is_exclusive = self.is_exclusive

        created_at = self.created_at

        modified_at = self.modified_at

        actions = []
        for actions_item_data in self.actions:
            actions_item = actions_item_data.to_dict()
            actions.append(actions_item)



        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        next_run_at: None | str | Unset
        if isinstance(self.next_run_at, Unset):
            next_run_at = UNSET
        else:
            next_run_at = self.next_run_at

        last_run_at: None | str | Unset
        if isinstance(self.last_run_at, Unset):
            last_run_at = UNSET
        else:
            last_run_at = self.last_run_at


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "userId": user_id,
            "name": name,
            "cronExpression": cron_expression,
            "timezone": timezone,
            "isEnabled": is_enabled,
            "isExclusive": is_exclusive,
            "createdAt": created_at,
            "modifiedAt": modified_at,
            "actions": actions,
        })
        if description is not UNSET:
            field_dict["description"] = description
        if next_run_at is not UNSET:
            field_dict["nextRunAt"] = next_run_at
        if last_run_at is not UNSET:
            field_dict["lastRunAt"] = last_run_at

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schedule_actions import ScheduleActions
        d = dict(src_dict)
        id = d.pop("id")

        user_id = d.pop("userId")

        name = d.pop("name")

        cron_expression = d.pop("cronExpression")

        timezone = d.pop("timezone")

        is_enabled = d.pop("isEnabled")

        is_exclusive = d.pop("isExclusive")

        created_at = d.pop("createdAt")

        modified_at = d.pop("modifiedAt")

        actions = []
        _actions = d.pop("actions")
        for actions_item_data in (_actions):
            actions_item = ScheduleActions.from_dict(actions_item_data)



            actions.append(actions_item)


        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))


        def _parse_next_run_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        next_run_at = _parse_next_run_at(d.pop("nextRunAt", UNSET))


        def _parse_last_run_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        last_run_at = _parse_last_run_at(d.pop("lastRunAt", UNSET))


        schedule = cls(
            id=id,
            user_id=user_id,
            name=name,
            cron_expression=cron_expression,
            timezone=timezone,
            is_enabled=is_enabled,
            is_exclusive=is_exclusive,
            created_at=created_at,
            modified_at=modified_at,
            actions=actions,
            description=description,
            next_run_at=next_run_at,
            last_run_at=last_run_at,
        )


        schedule.additional_properties = d
        return schedule

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
