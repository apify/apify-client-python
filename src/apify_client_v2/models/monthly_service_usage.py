from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
  from ..models.usage_item import UsageItem





T = TypeVar("T", bound="MonthlyServiceUsage")



@_attrs_define
class MonthlyServiceUsage:
    """ 
        Attributes:
            usage_item (UsageItem):
     """

    usage_item: UsageItem
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.usage_item import UsageItem
        usage_item = self.usage_item.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "USAGE_ITEM": usage_item,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.usage_item import UsageItem
        d = dict(src_dict)
        usage_item = UsageItem.from_dict(d.pop("USAGE_ITEM"))




        monthly_service_usage = cls(
            usage_item=usage_item,
        )


        monthly_service_usage.additional_properties = d
        return monthly_service_usage

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
