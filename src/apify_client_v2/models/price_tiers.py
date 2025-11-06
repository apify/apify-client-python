from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset







T = TypeVar("T", bound="PriceTiers")



@_attrs_define
class PriceTiers:
    """ 
        Attributes:
            quantity_above (float):
            discount_percent (float):  Example: 100.
            tier_quantity (float):  Example: 0.39.
            unit_price_usd (float):
            price_usd (float):
     """

    quantity_above: float
    discount_percent: float
    tier_quantity: float
    unit_price_usd: float
    price_usd: float
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        quantity_above = self.quantity_above

        discount_percent = self.discount_percent

        tier_quantity = self.tier_quantity

        unit_price_usd = self.unit_price_usd

        price_usd = self.price_usd


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "quantityAbove": quantity_above,
            "discountPercent": discount_percent,
            "tierQuantity": tier_quantity,
            "unitPriceUsd": unit_price_usd,
            "priceUsd": price_usd,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        quantity_above = d.pop("quantityAbove")

        discount_percent = d.pop("discountPercent")

        tier_quantity = d.pop("tierQuantity")

        unit_price_usd = d.pop("unitPriceUsd")

        price_usd = d.pop("priceUsd")

        price_tiers = cls(
            quantity_above=quantity_above,
            discount_percent=discount_percent,
            tier_quantity=tier_quantity,
            unit_price_usd=unit_price_usd,
            price_usd=price_usd,
        )


        price_tiers.additional_properties = d
        return price_tiers

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
