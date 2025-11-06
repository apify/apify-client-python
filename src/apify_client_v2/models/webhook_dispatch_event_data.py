from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset







T = TypeVar("T", bound="WebhookDispatchEventData")



@_attrs_define
class WebhookDispatchEventData:
    """ 
        Attributes:
            actor_id (str):  Example: vvE7iMKuMc5qTHHsR.
            actor_run_id (str):  Example: JgwXN9BdwxGcu9MMF.
     """

    actor_id: str
    actor_run_id: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        actor_id = self.actor_id

        actor_run_id = self.actor_run_id


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "actorId": actor_id,
            "actorRunId": actor_run_id,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        actor_id = d.pop("actorId")

        actor_run_id = d.pop("actorRunId")

        webhook_dispatch_event_data = cls(
            actor_id=actor_id,
            actor_run_id=actor_run_id,
        )


        webhook_dispatch_event_data.additional_properties = d
        return webhook_dispatch_event_data

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
