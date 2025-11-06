from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset







T = TypeVar("T", bound="ActUpdateTaggedBuildsType0AdditionalPropertyType0")



@_attrs_define
class ActUpdateTaggedBuildsType0AdditionalPropertyType0:
    """ 
        Attributes:
            build_id (str):
     """

    build_id: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        build_id = self.build_id


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "buildId": build_id,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        build_id = d.pop("buildId")

        act_update_tagged_builds_type_0_additional_property_type_0 = cls(
            build_id=build_id,
        )


        act_update_tagged_builds_type_0_additional_property_type_0.additional_properties = d
        return act_update_tagged_builds_type_0_additional_property_type_0

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
