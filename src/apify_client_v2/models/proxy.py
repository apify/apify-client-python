from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
  from ..models.proxy_group import ProxyGroup





T = TypeVar("T", bound="Proxy")



@_attrs_define
class Proxy:
    """ 
        Attributes:
            password (str):  Example: ad78knd9Jkjd86.
            groups (list[ProxyGroup]):
     """

    password: str
    groups: list[ProxyGroup]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.proxy_group import ProxyGroup
        password = self.password

        groups = []
        for groups_item_data in self.groups:
            groups_item = groups_item_data.to_dict()
            groups.append(groups_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "password": password,
            "groups": groups,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.proxy_group import ProxyGroup
        d = dict(src_dict)
        password = d.pop("password")

        groups = []
        _groups = d.pop("groups")
        for groups_item_data in (_groups):
            groups_item = ProxyGroup.from_dict(groups_item_data)



            groups.append(groups_item)


        proxy = cls(
            password=password,
            groups=groups,
        )


        proxy.additional_properties = d
        return proxy

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
