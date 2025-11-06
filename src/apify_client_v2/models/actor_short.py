from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset







T = TypeVar("T", bound="ActorShort")



@_attrs_define
class ActorShort:
    """ 
        Attributes:
            id (str):  Example: br9CKmk457.
            created_at (str):  Example: 2019-10-29T07:34:24.202Z.
            modified_at (str):  Example: 2019-10-30T07:34:24.202Z.
            name (str):  Example: MyAct.
            username (str):  Example: janedoe.
     """

    id: str
    created_at: str
    modified_at: str
    name: str
    username: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        id = self.id

        created_at = self.created_at

        modified_at = self.modified_at

        name = self.name

        username = self.username


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "createdAt": created_at,
            "modifiedAt": modified_at,
            "name": name,
            "username": username,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        created_at = d.pop("createdAt")

        modified_at = d.pop("modifiedAt")

        name = d.pop("name")

        username = d.pop("username")

        actor_short = cls(
            id=id,
            created_at=created_at,
            modified_at=modified_at,
            name=name,
            username=username,
        )


        actor_short.additional_properties = d
        return actor_short

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
