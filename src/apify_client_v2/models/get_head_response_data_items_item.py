from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset







T = TypeVar("T", bound="GetHeadResponseDataItemsItem")



@_attrs_define
class GetHeadResponseDataItemsItem:
    """ 
        Attributes:
            id (str):  Example: 8OamqXBCpPHxyH9.
            retry_count (float):
            unique_key (str):  Example: http://example.com.
            url (str):  Example: http://example.com.
            method (str):  Example: GET.
     """

    id: str
    retry_count: float
    unique_key: str
    url: str
    method: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        id = self.id

        retry_count = self.retry_count

        unique_key = self.unique_key

        url = self.url

        method = self.method


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "retryCount": retry_count,
            "uniqueKey": unique_key,
            "url": url,
            "method": method,
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

        get_head_response_data_items_item = cls(
            id=id,
            retry_count=retry_count,
            unique_key=unique_key,
            url=url,
            method=method,
        )


        get_head_response_data_items_item.additional_properties = d
        return get_head_response_data_items_item

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
