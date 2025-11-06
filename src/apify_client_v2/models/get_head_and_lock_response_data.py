from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.get_head_and_lock_response_data_items_item import GetHeadAndLockResponseDataItemsItem





T = TypeVar("T", bound="GetHeadAndLockResponseData")



@_attrs_define
class GetHeadAndLockResponseData:
    """ 
        Attributes:
            limit (float):  Example: 1000.
            queue_modified_at (str): The modifiedAt is updated whenever the queue is modified. Modifications include adding,
                updating, or removing requests, as well as locking or unlocking requests in the queue. Example:
                2018-03-14T23:00:00.000Z.
            had_multiple_clients (bool):  Example: True.
            lock_secs (float):  Example: 60.
            items (list[GetHeadAndLockResponseDataItemsItem]):
            queue_has_locked_requests (bool | Unset): Whether the queue contains requests locked by any client (either the
                one calling the endpoint or a different one). Example: True.
            client_key (str | Unset):  Example: client-one.
     """

    limit: float
    queue_modified_at: str
    had_multiple_clients: bool
    lock_secs: float
    items: list[GetHeadAndLockResponseDataItemsItem]
    queue_has_locked_requests: bool | Unset = UNSET
    client_key: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.get_head_and_lock_response_data_items_item import GetHeadAndLockResponseDataItemsItem
        limit = self.limit

        queue_modified_at = self.queue_modified_at

        had_multiple_clients = self.had_multiple_clients

        lock_secs = self.lock_secs

        items = []
        for items_item_data in self.items:
            items_item = items_item_data.to_dict()
            items.append(items_item)



        queue_has_locked_requests = self.queue_has_locked_requests

        client_key = self.client_key


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "limit": limit,
            "queueModifiedAt": queue_modified_at,
            "hadMultipleClients": had_multiple_clients,
            "lockSecs": lock_secs,
            "items": items,
        })
        if queue_has_locked_requests is not UNSET:
            field_dict["queueHasLockedRequests"] = queue_has_locked_requests
        if client_key is not UNSET:
            field_dict["clientKey"] = client_key

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_head_and_lock_response_data_items_item import GetHeadAndLockResponseDataItemsItem
        d = dict(src_dict)
        limit = d.pop("limit")

        queue_modified_at = d.pop("queueModifiedAt")

        had_multiple_clients = d.pop("hadMultipleClients")

        lock_secs = d.pop("lockSecs")

        items = []
        _items = d.pop("items")
        for items_item_data in (_items):
            items_item = GetHeadAndLockResponseDataItemsItem.from_dict(items_item_data)



            items.append(items_item)


        queue_has_locked_requests = d.pop("queueHasLockedRequests", UNSET)

        client_key = d.pop("clientKey", UNSET)

        get_head_and_lock_response_data = cls(
            limit=limit,
            queue_modified_at=queue_modified_at,
            had_multiple_clients=had_multiple_clients,
            lock_secs=lock_secs,
            items=items,
            queue_has_locked_requests=queue_has_locked_requests,
            client_key=client_key,
        )


        get_head_and_lock_response_data.additional_properties = d
        return get_head_and_lock_response_data

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
