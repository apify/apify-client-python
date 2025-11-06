from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.webhook_dispatch_event_data import WebhookDispatchEventData
  from ..models.webhook_dispatch_calls import WebhookDispatchCalls





T = TypeVar("T", bound="WebhookDispatch")



@_attrs_define
class WebhookDispatch:
    """ 
        Attributes:
            id (str):  Example: asdLZtadYvn4mBZmm.
            user_id (str):  Example: wRsJZtadYvn4mBZmm.
            webhook_id (str):  Example: asdLZtadYvn4mBZmm.
            created_at (str):  Example: 2019-12-12T07:34:14.202Z.
            status (str):  Example: SUCCEEDED.
            event_type (str):  Example: ACTOR.RUN.SUCCEEDED.
            event_data (WebhookDispatchEventData):
            calls (WebhookDispatchCalls | Unset):
     """

    id: str
    user_id: str
    webhook_id: str
    created_at: str
    status: str
    event_type: str
    event_data: WebhookDispatchEventData
    calls: WebhookDispatchCalls | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.webhook_dispatch_event_data import WebhookDispatchEventData
        from ..models.webhook_dispatch_calls import WebhookDispatchCalls
        id = self.id

        user_id = self.user_id

        webhook_id = self.webhook_id

        created_at = self.created_at

        status = self.status

        event_type = self.event_type

        event_data = self.event_data.to_dict()

        calls: dict[str, Any] | Unset = UNSET
        if not isinstance(self.calls, Unset):
            calls = self.calls.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "userId": user_id,
            "webhookId": webhook_id,
            "createdAt": created_at,
            "status": status,
            "eventType": event_type,
            "eventData": event_data,
        })
        if calls is not UNSET:
            field_dict["calls"] = calls

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.webhook_dispatch_event_data import WebhookDispatchEventData
        from ..models.webhook_dispatch_calls import WebhookDispatchCalls
        d = dict(src_dict)
        id = d.pop("id")

        user_id = d.pop("userId")

        webhook_id = d.pop("webhookId")

        created_at = d.pop("createdAt")

        status = d.pop("status")

        event_type = d.pop("eventType")

        event_data = WebhookDispatchEventData.from_dict(d.pop("eventData"))




        _calls = d.pop("calls", UNSET)
        calls: WebhookDispatchCalls | Unset
        if isinstance(_calls,  Unset):
            calls = UNSET
        else:
            calls = WebhookDispatchCalls.from_dict(_calls)




        webhook_dispatch = cls(
            id=id,
            user_id=user_id,
            webhook_id=webhook_id,
            created_at=created_at,
            status=status,
            event_type=event_type,
            event_data=event_data,
            calls=calls,
        )


        webhook_dispatch.additional_properties = d
        return webhook_dispatch

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
