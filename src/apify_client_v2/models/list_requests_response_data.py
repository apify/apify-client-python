from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.request_queue_items import RequestQueueItems





T = TypeVar("T", bound="ListRequestsResponseData")



@_attrs_define
class ListRequestsResponseData:
    """ 
        Attributes:
            items (list[RequestQueueItems]):
            count (float):  Example: 2.
            limit (float):  Example: 2.
            exclusive_start_id (str | Unset):  Example: Ihnsp8YrvJ8102Kj.
     """

    items: list[RequestQueueItems]
    count: float
    limit: float
    exclusive_start_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.request_queue_items import RequestQueueItems
        items = []
        for items_item_data in self.items:
            items_item = items_item_data.to_dict()
            items.append(items_item)



        count = self.count

        limit = self.limit

        exclusive_start_id = self.exclusive_start_id


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "items": items,
            "count": count,
            "limit": limit,
        })
        if exclusive_start_id is not UNSET:
            field_dict["exclusiveStartId"] = exclusive_start_id

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.request_queue_items import RequestQueueItems
        d = dict(src_dict)
        items = []
        _items = d.pop("items")
        for items_item_data in (_items):
            items_item = RequestQueueItems.from_dict(items_item_data)



            items.append(items_item)


        count = d.pop("count")

        limit = d.pop("limit")

        exclusive_start_id = d.pop("exclusiveStartId", UNSET)

        list_requests_response_data = cls(
            items=items,
            count=count,
            limit=limit,
            exclusive_start_id=exclusive_start_id,
        )


        list_requests_response_data.additional_properties = d
        return list_requests_response_data

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
