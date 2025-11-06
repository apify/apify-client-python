from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.list_of_keys_response_items import ListOfKeysResponseItems





T = TypeVar("T", bound="ListOfKeysResponse")



@_attrs_define
class ListOfKeysResponse:
    """ 
        Attributes:
            items (list[ListOfKeysResponseItems]):
            count (float):  Example: 2.
            limit (float):  Example: 2.
            is_truncated (bool):  Example: True.
            exclusive_start_key (str | Unset):  Example: some-key.
            next_exclusive_start_key (str | Unset):  Example: third-key.
     """

    items: list[ListOfKeysResponseItems]
    count: float
    limit: float
    is_truncated: bool
    exclusive_start_key: str | Unset = UNSET
    next_exclusive_start_key: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.list_of_keys_response_items import ListOfKeysResponseItems
        items = []
        for items_item_data in self.items:
            items_item = items_item_data.to_dict()
            items.append(items_item)



        count = self.count

        limit = self.limit

        is_truncated = self.is_truncated

        exclusive_start_key = self.exclusive_start_key

        next_exclusive_start_key = self.next_exclusive_start_key


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "items": items,
            "count": count,
            "limit": limit,
            "isTruncated": is_truncated,
        })
        if exclusive_start_key is not UNSET:
            field_dict["exclusiveStartKey"] = exclusive_start_key
        if next_exclusive_start_key is not UNSET:
            field_dict["nextExclusiveStartKey"] = next_exclusive_start_key

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.list_of_keys_response_items import ListOfKeysResponseItems
        d = dict(src_dict)
        items = []
        _items = d.pop("items")
        for items_item_data in (_items):
            items_item = ListOfKeysResponseItems.from_dict(items_item_data)



            items.append(items_item)


        count = d.pop("count")

        limit = d.pop("limit")

        is_truncated = d.pop("isTruncated")

        exclusive_start_key = d.pop("exclusiveStartKey", UNSET)

        next_exclusive_start_key = d.pop("nextExclusiveStartKey", UNSET)

        list_of_keys_response = cls(
            items=items,
            count=count,
            limit=limit,
            is_truncated=is_truncated,
            exclusive_start_key=exclusive_start_key,
            next_exclusive_start_key=next_exclusive_start_key,
        )


        list_of_keys_response.additional_properties = d
        return list_of_keys_response

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
