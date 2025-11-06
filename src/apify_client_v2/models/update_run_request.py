from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset






T = TypeVar("T", bound="UpdateRunRequest")



@_attrs_define
class UpdateRunRequest:
    """ 
        Attributes:
            run_id (str):  Example: 3KH8gEpp4d8uQSe8T.
            status_message (str):  Example: Actor has finished.
            is_status_message_terminal (bool | Unset):  Example: True.
     """

    run_id: str
    status_message: str
    is_status_message_terminal: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        run_id = self.run_id

        status_message = self.status_message

        is_status_message_terminal = self.is_status_message_terminal


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "runId": run_id,
            "statusMessage": status_message,
        })
        if is_status_message_terminal is not UNSET:
            field_dict["isStatusMessageTerminal"] = is_status_message_terminal

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        run_id = d.pop("runId")

        status_message = d.pop("statusMessage")

        is_status_message_terminal = d.pop("isStatusMessageTerminal", UNSET)

        update_run_request = cls(
            run_id=run_id,
            status_message=status_message,
            is_status_message_terminal=is_status_message_terminal,
        )


        update_run_request.additional_properties = d
        return update_run_request

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
