from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset







T = TypeVar("T", bound="ProcessedRequest")



@_attrs_define
class ProcessedRequest:
    """ 
        Attributes:
            request_id (str):  Example: sbJ7klsdf7ujN9l.
            unique_key (str):  Example: http://example.com.
            was_already_present (bool):
            was_already_handled (bool):
     """

    request_id: str
    unique_key: str
    was_already_present: bool
    was_already_handled: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        request_id = self.request_id

        unique_key = self.unique_key

        was_already_present = self.was_already_present

        was_already_handled = self.was_already_handled


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "requestId": request_id,
            "uniqueKey": unique_key,
            "wasAlreadyPresent": was_already_present,
            "wasAlreadyHandled": was_already_handled,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        request_id = d.pop("requestId")

        unique_key = d.pop("uniqueKey")

        was_already_present = d.pop("wasAlreadyPresent")

        was_already_handled = d.pop("wasAlreadyHandled")

        processed_request = cls(
            request_id=request_id,
            unique_key=unique_key,
            was_already_present=was_already_present,
            was_already_handled=was_already_handled,
        )


        processed_request.additional_properties = d
        return processed_request

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
