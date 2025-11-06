from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset







T = TypeVar("T", bound="ProlongRequestLockResponseData")



@_attrs_define
class ProlongRequestLockResponseData:
    """ 
        Attributes:
            lock_expires_at (str): Date when lock expires. Example: 2022-01-01T00:00:00.000Z.
     """

    lock_expires_at: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        lock_expires_at = self.lock_expires_at


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "lockExpiresAt": lock_expires_at,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        lock_expires_at = d.pop("lockExpiresAt")

        prolong_request_lock_response_data = cls(
            lock_expires_at=lock_expires_at,
        )


        prolong_request_lock_response_data.additional_properties = d
        return prolong_request_lock_response_data

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
