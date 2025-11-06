from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
  from ..models.price_tiers import PriceTiers





T = TypeVar("T", bound="UsageItem")



@_attrs_define
class UsageItem:
    """ 
        Attributes:
            quantity (float):  Example: 2.784475.
            base_amount_usd (float):  Example: 0.69611875.
            base_unit_price_usd (float):  Example: 0.25.
            amount_after_volume_discount_usd (float):  Example: 0.69611875.
            price_tiers (list[PriceTiers]):
     """

    quantity: float
    base_amount_usd: float
    base_unit_price_usd: float
    amount_after_volume_discount_usd: float
    price_tiers: list[PriceTiers]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.price_tiers import PriceTiers
        quantity = self.quantity

        base_amount_usd = self.base_amount_usd

        base_unit_price_usd = self.base_unit_price_usd

        amount_after_volume_discount_usd = self.amount_after_volume_discount_usd

        price_tiers = []
        for price_tiers_item_data in self.price_tiers:
            price_tiers_item = price_tiers_item_data.to_dict()
            price_tiers.append(price_tiers_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "quantity": quantity,
            "baseAmountUsd": base_amount_usd,
            "baseUnitPriceUsd": base_unit_price_usd,
            "amountAfterVolumeDiscountUsd": amount_after_volume_discount_usd,
            "priceTiers": price_tiers,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.price_tiers import PriceTiers
        d = dict(src_dict)
        quantity = d.pop("quantity")

        base_amount_usd = d.pop("baseAmountUsd")

        base_unit_price_usd = d.pop("baseUnitPriceUsd")

        amount_after_volume_discount_usd = d.pop("amountAfterVolumeDiscountUsd")

        price_tiers = []
        _price_tiers = d.pop("priceTiers")
        for price_tiers_item_data in (_price_tiers):
            price_tiers_item = PriceTiers.from_dict(price_tiers_item_data)



            price_tiers.append(price_tiers_item)


        usage_item = cls(
            quantity=quantity,
            base_amount_usd=base_amount_usd,
            base_unit_price_usd=base_unit_price_usd,
            amount_after_volume_discount_usd=amount_after_volume_discount_usd,
            price_tiers=price_tiers,
        )


        usage_item.additional_properties = d
        return usage_item

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
