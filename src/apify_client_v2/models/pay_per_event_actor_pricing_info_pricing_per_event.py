from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.pay_per_event_actor_pricing_info_pricing_per_event_actor_charge_events import PayPerEventActorPricingInfoPricingPerEventActorChargeEvents





T = TypeVar("T", bound="PayPerEventActorPricingInfoPricingPerEvent")



@_attrs_define
class PayPerEventActorPricingInfoPricingPerEvent:
    """ 
        Attributes:
            actor_charge_events (PayPerEventActorPricingInfoPricingPerEventActorChargeEvents | Unset):
     """

    actor_charge_events: PayPerEventActorPricingInfoPricingPerEventActorChargeEvents | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.pay_per_event_actor_pricing_info_pricing_per_event_actor_charge_events import PayPerEventActorPricingInfoPricingPerEventActorChargeEvents
        actor_charge_events: dict[str, Any] | Unset = UNSET
        if not isinstance(self.actor_charge_events, Unset):
            actor_charge_events = self.actor_charge_events.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if actor_charge_events is not UNSET:
            field_dict["actorChargeEvents"] = actor_charge_events

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.pay_per_event_actor_pricing_info_pricing_per_event_actor_charge_events import PayPerEventActorPricingInfoPricingPerEventActorChargeEvents
        d = dict(src_dict)
        _actor_charge_events = d.pop("actorChargeEvents", UNSET)
        actor_charge_events: PayPerEventActorPricingInfoPricingPerEventActorChargeEvents | Unset
        if isinstance(_actor_charge_events,  Unset):
            actor_charge_events = UNSET
        else:
            actor_charge_events = PayPerEventActorPricingInfoPricingPerEventActorChargeEvents.from_dict(_actor_charge_events)




        pay_per_event_actor_pricing_info_pricing_per_event = cls(
            actor_charge_events=actor_charge_events,
        )


        pay_per_event_actor_pricing_info_pricing_per_event.additional_properties = d
        return pay_per_event_actor_pricing_info_pricing_per_event

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
