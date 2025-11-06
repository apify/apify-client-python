from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
  from ..models.env_var import EnvVar





T = TypeVar("T", bound="GetEnvVarListResponseData")



@_attrs_define
class GetEnvVarListResponseData:
    """ 
        Attributes:
            total (float):  Example: 5.
            items (list[EnvVar]):
     """

    total: float
    items: list[EnvVar]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.env_var import EnvVar
        total = self.total

        items = []
        for items_item_data in self.items:
            items_item = items_item_data.to_dict()
            items.append(items_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "total": total,
            "items": items,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.env_var import EnvVar
        d = dict(src_dict)
        total = d.pop("total")

        items = []
        _items = d.pop("items")
        for items_item_data in (_items):
            items_item = EnvVar.from_dict(items_item_data)



            items.append(items_item)


        get_env_var_list_response_data = cls(
            total=total,
            items=items,
        )


        get_env_var_list_response_data.additional_properties = d
        return get_env_var_list_response_data

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
