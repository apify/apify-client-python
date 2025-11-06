from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset







T = TypeVar("T", bound="ListOfKeysResponseItems")



@_attrs_define
class ListOfKeysResponseItems:
    """ 
        Attributes:
            key (str):  Example: second-key.
            size (float):  Example: 36.
            record_public_url (str): A public link to access this record directly. Example: https://api.apify.com/v2/key-
                value-stores/WkzbQMuFYuamGv3YF/records/some-key?signature=abc123.
     """

    key: str
    size: float
    record_public_url: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        key = self.key

        size = self.size

        record_public_url = self.record_public_url


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "key": key,
            "size": size,
            "recordPublicUrl": record_public_url,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        key = d.pop("key")

        size = d.pop("size")

        record_public_url = d.pop("recordPublicUrl")

        list_of_keys_response_items = cls(
            key=key,
            size=size,
            record_public_url=record_public_url,
        )


        list_of_keys_response_items.additional_properties = d
        return list_of_keys_response_items

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
