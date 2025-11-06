from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset







T = TypeVar("T", bound="ActorChargeEvent")



@_attrs_define
class ActorChargeEvent:
    """ 
        Attributes:
            event_price_usd (float):
            event_title (str):
            event_description (str):
     """

    event_price_usd: float
    event_title: str
    event_description: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        event_price_usd = self.event_price_usd

        event_title = self.event_title

        event_description = self.event_description


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "eventPriceUsd": event_price_usd,
            "eventTitle": event_title,
            "eventDescription": event_description,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        event_price_usd = d.pop("eventPriceUsd")

        event_title = d.pop("eventTitle")

        event_description = d.pop("eventDescription")

        actor_charge_event = cls(
            event_price_usd=event_price_usd,
            event_title=event_title,
            event_description=event_description,
        )


        actor_charge_event.additional_properties = d
        return actor_charge_event

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
