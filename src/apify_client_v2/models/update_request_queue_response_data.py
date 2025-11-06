from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset






T = TypeVar("T", bound="UpdateRequestQueueResponseData")



@_attrs_define
class UpdateRequestQueueResponseData:
    """ 
        Attributes:
            id (str):  Example: WkzbQMuFYuamGv3YF.
            user_id (str):  Example: wRsJZtadYvn4mBZmm.
            created_at (str):  Example: 2019-12-12T07:34:14.202Z.
            modified_at (str): The modifiedAt is updated whenever the queue is modified. Modifications include adding,
                updating, or removing requests, as well as locking or unlocking requests in the queue. Example:
                2030-12-13T08:36:13.202Z.
            accessed_at (str):  Example: 2019-12-14T08:36:13.202Z.
            total_request_count (float):  Example: 870.
            handled_request_count (float):  Example: 100.
            pending_request_count (float):  Example: 670.
            had_multiple_clients (bool):  Example: True.
            console_url (str):  Example: https://api.apify.com/v2/request-queues/27TmTznX9YPeAYhkC.
            name (str | Unset):  Example: some-name.
     """

    id: str
    user_id: str
    created_at: str
    modified_at: str
    accessed_at: str
    total_request_count: float
    handled_request_count: float
    pending_request_count: float
    had_multiple_clients: bool
    console_url: str
    name: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        id = self.id

        user_id = self.user_id

        created_at = self.created_at

        modified_at = self.modified_at

        accessed_at = self.accessed_at

        total_request_count = self.total_request_count

        handled_request_count = self.handled_request_count

        pending_request_count = self.pending_request_count

        had_multiple_clients = self.had_multiple_clients

        console_url = self.console_url

        name = self.name


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "userId": user_id,
            "createdAt": created_at,
            "modifiedAt": modified_at,
            "accessedAt": accessed_at,
            "totalRequestCount": total_request_count,
            "handledRequestCount": handled_request_count,
            "pendingRequestCount": pending_request_count,
            "hadMultipleClients": had_multiple_clients,
            "consoleUrl": console_url,
        })
        if name is not UNSET:
            field_dict["name"] = name

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        user_id = d.pop("userId")

        created_at = d.pop("createdAt")

        modified_at = d.pop("modifiedAt")

        accessed_at = d.pop("accessedAt")

        total_request_count = d.pop("totalRequestCount")

        handled_request_count = d.pop("handledRequestCount")

        pending_request_count = d.pop("pendingRequestCount")

        had_multiple_clients = d.pop("hadMultipleClients")

        console_url = d.pop("consoleUrl")

        name = d.pop("name", UNSET)

        update_request_queue_response_data = cls(
            id=id,
            user_id=user_id,
            created_at=created_at,
            modified_at=modified_at,
            accessed_at=accessed_at,
            total_request_count=total_request_count,
            handled_request_count=handled_request_count,
            pending_request_count=pending_request_count,
            had_multiple_clients=had_multiple_clients,
            console_url=console_url,
            name=name,
        )


        update_request_queue_response_data.additional_properties = d
        return update_request_queue_response_data

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
