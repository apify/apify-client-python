from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset







T = TypeVar("T", bound="PaginationResponse")



@_attrs_define
class PaginationResponse:
    """ 
        Attributes:
            total (float):  Example: 2.
            offset (float):
            limit (float):  Example: 1000.
            desc (bool):
            count (float):  Example: 2.
     """

    total: float
    offset: float
    limit: float
    desc: bool
    count: float
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        total = self.total

        offset = self.offset

        limit = self.limit

        desc = self.desc

        count = self.count


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "total": total,
            "offset": offset,
            "limit": limit,
            "desc": desc,
            "count": count,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        total = d.pop("total")

        offset = d.pop("offset")

        limit = d.pop("limit")

        desc = d.pop("desc")

        count = d.pop("count")

        pagination_response = cls(
            total=total,
            offset=offset,
            limit=limit,
            desc=desc,
            count=count,
        )


        pagination_response.additional_properties = d
        return pagination_response

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
