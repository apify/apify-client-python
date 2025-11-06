from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast






T = TypeVar("T", bound="RequestQueueShort")



@_attrs_define
class RequestQueueShort:
    """ 
        Attributes:
            id (str):  Example: WkzbQMuFYuamGv3YF.
            name (str):  Example: some-name.
            user_id (str):  Example: wRsJZtadYvn4mBZmm.
            username (str):  Example: janedoe.
            created_at (str):  Example: 2019-12-12T07:34:14.202Z.
            modified_at (str):  Example: 2019-12-13T08:36:13.202Z.
            accessed_at (str):  Example: 2019-12-14T08:36:13.202Z.
            expire_at (str):  Example: 2019-06-02T17:15:06.751Z.
            total_request_count (float):  Example: 100.
            handled_request_count (float):  Example: 50.
            pending_request_count (float):  Example: 50.
            had_multiple_clients (bool):  Example: True.
            act_id (None | str | Unset):
            act_run_id (None | str | Unset):
     """

    id: str
    name: str
    user_id: str
    username: str
    created_at: str
    modified_at: str
    accessed_at: str
    expire_at: str
    total_request_count: float
    handled_request_count: float
    pending_request_count: float
    had_multiple_clients: bool
    act_id: None | str | Unset = UNSET
    act_run_id: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        user_id = self.user_id

        username = self.username

        created_at = self.created_at

        modified_at = self.modified_at

        accessed_at = self.accessed_at

        expire_at = self.expire_at

        total_request_count = self.total_request_count

        handled_request_count = self.handled_request_count

        pending_request_count = self.pending_request_count

        had_multiple_clients = self.had_multiple_clients

        act_id: None | str | Unset
        if isinstance(self.act_id, Unset):
            act_id = UNSET
        else:
            act_id = self.act_id

        act_run_id: None | str | Unset
        if isinstance(self.act_run_id, Unset):
            act_run_id = UNSET
        else:
            act_run_id = self.act_run_id


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "name": name,
            "userId": user_id,
            "username": username,
            "createdAt": created_at,
            "modifiedAt": modified_at,
            "accessedAt": accessed_at,
            "expireAt": expire_at,
            "totalRequestCount": total_request_count,
            "handledRequestCount": handled_request_count,
            "pendingRequestCount": pending_request_count,
            "hadMultipleClients": had_multiple_clients,
        })
        if act_id is not UNSET:
            field_dict["actId"] = act_id
        if act_run_id is not UNSET:
            field_dict["actRunId"] = act_run_id

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        user_id = d.pop("userId")

        username = d.pop("username")

        created_at = d.pop("createdAt")

        modified_at = d.pop("modifiedAt")

        accessed_at = d.pop("accessedAt")

        expire_at = d.pop("expireAt")

        total_request_count = d.pop("totalRequestCount")

        handled_request_count = d.pop("handledRequestCount")

        pending_request_count = d.pop("pendingRequestCount")

        had_multiple_clients = d.pop("hadMultipleClients")

        def _parse_act_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        act_id = _parse_act_id(d.pop("actId", UNSET))


        def _parse_act_run_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        act_run_id = _parse_act_run_id(d.pop("actRunId", UNSET))


        request_queue_short = cls(
            id=id,
            name=name,
            user_id=user_id,
            username=username,
            created_at=created_at,
            modified_at=modified_at,
            accessed_at=accessed_at,
            expire_at=expire_at,
            total_request_count=total_request_count,
            handled_request_count=handled_request_count,
            pending_request_count=pending_request_count,
            had_multiple_clients=had_multiple_clients,
            act_id=act_id,
            act_run_id=act_run_id,
        )


        request_queue_short.additional_properties = d
        return request_queue_short

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
