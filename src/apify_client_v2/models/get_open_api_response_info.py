from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset






T = TypeVar("T", bound="GetOpenApiResponseInfo")



@_attrs_define
class GetOpenApiResponseInfo:
    """ 
        Attributes:
            title (str | Unset):  Example: Your Magic Actor.
            version (str | Unset):  Example: 1.0.
            x_build_id (str | Unset):  Example: ID of build.
     """

    title: str | Unset = UNSET
    version: str | Unset = UNSET
    x_build_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        title = self.title

        version = self.version

        x_build_id = self.x_build_id


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if title is not UNSET:
            field_dict["title"] = title
        if version is not UNSET:
            field_dict["version"] = version
        if x_build_id is not UNSET:
            field_dict["x-build-id"] = x_build_id

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        title = d.pop("title", UNSET)

        version = d.pop("version", UNSET)

        x_build_id = d.pop("x-build-id", UNSET)

        get_open_api_response_info = cls(
            title=title,
            version=version,
            x_build_id=x_build_id,
        )


        get_open_api_response_info.additional_properties = d
        return get_open_api_response_info

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
