from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset







T = TypeVar("T", bound="BuildShortMeta")



@_attrs_define
class BuildShortMeta:
    """ 
        Attributes:
            origin (str):  Example: WEB.
            client_ip (str):  Example: 172.234.12.34.
            user_agent (str):  Example: Mozilla/5.0 (iPad).
     """

    origin: str
    client_ip: str
    user_agent: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        origin = self.origin

        client_ip = self.client_ip

        user_agent = self.user_agent


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "origin": origin,
            "clientIp": client_ip,
            "userAgent": user_agent,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        origin = d.pop("origin")

        client_ip = d.pop("clientIp")

        user_agent = d.pop("userAgent")

        build_short_meta = cls(
            origin=origin,
            client_ip=client_ip,
            user_agent=user_agent,
        )


        build_short_meta.additional_properties = d
        return build_short_meta

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
