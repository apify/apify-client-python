from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset







T = TypeVar("T", bound="GetHeadAndLockResponseDataItemsItem")



@_attrs_define
class GetHeadAndLockResponseDataItemsItem:
    """ 
        Attributes:
            id (str):  Example: 8OamqXBCpPHxyj9.
            retry_count (float):
            unique_key (str):  Example: http://example.com.
            url (str):  Example: http://example.com.
            method (str):  Example: GET.
            lock_expires_at (str):  Example: 2022-06-14T23:00:00.000Z.
     """

    id: str
    retry_count: float
    unique_key: str
    url: str
    method: str
    lock_expires_at: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        id = self.id

        retry_count = self.retry_count

        unique_key = self.unique_key

        url = self.url

        method = self.method

        lock_expires_at = self.lock_expires_at


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "retryCount": retry_count,
            "uniqueKey": unique_key,
            "url": url,
            "method": method,
            "lockExpiresAt": lock_expires_at,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        retry_count = d.pop("retryCount")

        unique_key = d.pop("uniqueKey")

        url = d.pop("url")

        method = d.pop("method")

        lock_expires_at = d.pop("lockExpiresAt")

        get_head_and_lock_response_data_items_item = cls(
            id=id,
            retry_count=retry_count,
            unique_key=unique_key,
            url=url,
            method=method,
            lock_expires_at=lock_expires_at,
        )


        get_head_and_lock_response_data_items_item.additional_properties = d
        return get_head_and_lock_response_data_items_item

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
