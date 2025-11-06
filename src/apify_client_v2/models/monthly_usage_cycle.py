from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset







T = TypeVar("T", bound="MonthlyUsageCycle")



@_attrs_define
class MonthlyUsageCycle:
    """ 
        Attributes:
            start_at (str):  Example: 2022-10-02T00:00:00.000Z.
            end_at (str):  Example: 2022-11-01T23:59:59.999Z.
     """

    start_at: str
    end_at: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        start_at = self.start_at

        end_at = self.end_at


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "startAt": start_at,
            "endAt": end_at,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        start_at = d.pop("startAt")

        end_at = d.pop("endAt")

        monthly_usage_cycle = cls(
            start_at=start_at,
            end_at=end_at,
        )


        monthly_usage_cycle.additional_properties = d
        return monthly_usage_cycle

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
