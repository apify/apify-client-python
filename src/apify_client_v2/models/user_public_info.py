from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
  from ..models.profile import Profile





T = TypeVar("T", bound="UserPublicInfo")



@_attrs_define
class UserPublicInfo:
    """ 
        Attributes:
            username (str):  Example: d7b9MDYsbtX5L7XAj.
            profile (Profile):
     """

    username: str
    profile: Profile
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.profile import Profile
        username = self.username

        profile = self.profile.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "username": username,
            "profile": profile,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.profile import Profile
        d = dict(src_dict)
        username = d.pop("username")

        profile = Profile.from_dict(d.pop("profile"))




        user_public_info = cls(
            username=username,
            profile=profile,
        )


        user_public_info.additional_properties = d
        return user_public_info

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
