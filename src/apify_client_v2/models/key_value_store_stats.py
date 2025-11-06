from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset







T = TypeVar("T", bound="KeyValueStoreStats")



@_attrs_define
class KeyValueStoreStats:
    """ 
        Attributes:
            read_count (float):  Example: 9.
            write_count (float):  Example: 3.
            delete_count (float):  Example: 6.
            list_count (float):  Example: 2.
            s_3_storage_bytes (float):  Example: 18.
     """

    read_count: float
    write_count: float
    delete_count: float
    list_count: float
    s_3_storage_bytes: float
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        read_count = self.read_count

        write_count = self.write_count

        delete_count = self.delete_count

        list_count = self.list_count

        s_3_storage_bytes = self.s_3_storage_bytes


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "readCount": read_count,
            "writeCount": write_count,
            "deleteCount": delete_count,
            "listCount": list_count,
            "s3StorageBytes": s_3_storage_bytes,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        read_count = d.pop("readCount")

        write_count = d.pop("writeCount")

        delete_count = d.pop("deleteCount")

        list_count = d.pop("listCount")

        s_3_storage_bytes = d.pop("s3StorageBytes")

        key_value_store_stats = cls(
            read_count=read_count,
            write_count=write_count,
            delete_count=delete_count,
            list_count=list_count,
            s_3_storage_bytes=s_3_storage_bytes,
        )


        key_value_store_stats.additional_properties = d
        return key_value_store_stats

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
