from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.schedule_actions_run_input import ScheduleActionsRunInput
  from ..models.schedule_actions_run_options import ScheduleActionsRunOptions





T = TypeVar("T", bound="ScheduleActions")



@_attrs_define
class ScheduleActions:
    """ 
        Attributes:
            id (str):  Example: c6KfSgoQzFhMk3etc.
            type_ (str):  Example: RUN_ACTOR.
            actor_id (str):  Example: jF8GGEvbEg4Au3NLA.
            run_input (None | ScheduleActionsRunInput | Unset):
            run_options (None | ScheduleActionsRunOptions | Unset):
     """

    id: str
    type_: str
    actor_id: str
    run_input: None | ScheduleActionsRunInput | Unset = UNSET
    run_options: None | ScheduleActionsRunOptions | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.schedule_actions_run_input import ScheduleActionsRunInput
        from ..models.schedule_actions_run_options import ScheduleActionsRunOptions
        id = self.id

        type_ = self.type_

        actor_id = self.actor_id

        run_input: dict[str, Any] | None | Unset
        if isinstance(self.run_input, Unset):
            run_input = UNSET
        elif isinstance(self.run_input, ScheduleActionsRunInput):
            run_input = self.run_input.to_dict()
        else:
            run_input = self.run_input

        run_options: dict[str, Any] | None | Unset
        if isinstance(self.run_options, Unset):
            run_options = UNSET
        elif isinstance(self.run_options, ScheduleActionsRunOptions):
            run_options = self.run_options.to_dict()
        else:
            run_options = self.run_options


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "type": type_,
            "actorId": actor_id,
        })
        if run_input is not UNSET:
            field_dict["runInput"] = run_input
        if run_options is not UNSET:
            field_dict["runOptions"] = run_options

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schedule_actions_run_input import ScheduleActionsRunInput
        from ..models.schedule_actions_run_options import ScheduleActionsRunOptions
        d = dict(src_dict)
        id = d.pop("id")

        type_ = d.pop("type")

        actor_id = d.pop("actorId")

        def _parse_run_input(data: object) -> None | ScheduleActionsRunInput | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                run_input_type_1 = ScheduleActionsRunInput.from_dict(data)



                return run_input_type_1
            except: # noqa: E722
                pass
            return cast(None | ScheduleActionsRunInput | Unset, data)

        run_input = _parse_run_input(d.pop("runInput", UNSET))


        def _parse_run_options(data: object) -> None | ScheduleActionsRunOptions | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                run_options_type_1 = ScheduleActionsRunOptions.from_dict(data)



                return run_options_type_1
            except: # noqa: E722
                pass
            return cast(None | ScheduleActionsRunOptions | Unset, data)

        run_options = _parse_run_options(d.pop("runOptions", UNSET))


        schedule_actions = cls(
            id=id,
            type_=type_,
            actor_id=actor_id,
            run_input=run_input,
            run_options=run_options,
        )


        schedule_actions.additional_properties = d
        return schedule_actions

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
