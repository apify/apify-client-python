from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.create_schedule_actions import CreateScheduleActions





T = TypeVar("T", bound="ScheduleCreate")



@_attrs_define
class ScheduleCreate:
    """ 
        Attributes:
            name (None | str | Unset):  Example: my-schedule.
            is_enabled (bool | None | Unset):  Example: True.
            is_exclusive (bool | None | Unset):  Example: True.
            cron_expression (None | str | Unset):  Example: * * * * *.
            timezone (None | str | Unset):  Example: UTC.
            description (None | str | Unset):  Example: Schedule of actor ....
            actions (list[CreateScheduleActions] | None | Unset):
     """

    name: None | str | Unset = UNSET
    is_enabled: bool | None | Unset = UNSET
    is_exclusive: bool | None | Unset = UNSET
    cron_expression: None | str | Unset = UNSET
    timezone: None | str | Unset = UNSET
    description: None | str | Unset = UNSET
    actions: list[CreateScheduleActions] | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.create_schedule_actions import CreateScheduleActions
        name: None | str | Unset
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        is_enabled: bool | None | Unset
        if isinstance(self.is_enabled, Unset):
            is_enabled = UNSET
        else:
            is_enabled = self.is_enabled

        is_exclusive: bool | None | Unset
        if isinstance(self.is_exclusive, Unset):
            is_exclusive = UNSET
        else:
            is_exclusive = self.is_exclusive

        cron_expression: None | str | Unset
        if isinstance(self.cron_expression, Unset):
            cron_expression = UNSET
        else:
            cron_expression = self.cron_expression

        timezone: None | str | Unset
        if isinstance(self.timezone, Unset):
            timezone = UNSET
        else:
            timezone = self.timezone

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        actions: list[dict[str, Any]] | None | Unset
        if isinstance(self.actions, Unset):
            actions = UNSET
        elif isinstance(self.actions, list):
            actions = []
            for actions_type_0_item_data in self.actions:
                actions_type_0_item = actions_type_0_item_data.to_dict()
                actions.append(actions_type_0_item)


        else:
            actions = self.actions


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if name is not UNSET:
            field_dict["name"] = name
        if is_enabled is not UNSET:
            field_dict["isEnabled"] = is_enabled
        if is_exclusive is not UNSET:
            field_dict["isExclusive"] = is_exclusive
        if cron_expression is not UNSET:
            field_dict["cronExpression"] = cron_expression
        if timezone is not UNSET:
            field_dict["timezone"] = timezone
        if description is not UNSET:
            field_dict["description"] = description
        if actions is not UNSET:
            field_dict["actions"] = actions

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.create_schedule_actions import CreateScheduleActions
        d = dict(src_dict)
        def _parse_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        name = _parse_name(d.pop("name", UNSET))


        def _parse_is_enabled(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        is_enabled = _parse_is_enabled(d.pop("isEnabled", UNSET))


        def _parse_is_exclusive(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        is_exclusive = _parse_is_exclusive(d.pop("isExclusive", UNSET))


        def _parse_cron_expression(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        cron_expression = _parse_cron_expression(d.pop("cronExpression", UNSET))


        def _parse_timezone(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        timezone = _parse_timezone(d.pop("timezone", UNSET))


        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))


        def _parse_actions(data: object) -> list[CreateScheduleActions] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                actions_type_0 = []
                _actions_type_0 = data
                for actions_type_0_item_data in (_actions_type_0):
                    actions_type_0_item = CreateScheduleActions.from_dict(actions_type_0_item_data)



                    actions_type_0.append(actions_type_0_item)

                return actions_type_0
            except: # noqa: E722
                pass
            return cast(list[CreateScheduleActions] | None | Unset, data)

        actions = _parse_actions(d.pop("actions", UNSET))


        schedule_create = cls(
            name=name,
            is_enabled=is_enabled,
            is_exclusive=is_exclusive,
            cron_expression=cron_expression,
            timezone=timezone,
            description=description,
            actions=actions,
        )


        schedule_create.additional_properties = d
        return schedule_create

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
