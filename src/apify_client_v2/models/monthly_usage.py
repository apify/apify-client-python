from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
  from ..models.monthly_service_usage import MonthlyServiceUsage
  from ..models.usage_cycle import UsageCycle
  from ..models.daily_service_usages import DailyServiceUsages





T = TypeVar("T", bound="MonthlyUsage")



@_attrs_define
class MonthlyUsage:
    """ 
        Attributes:
            usage_cycle (UsageCycle):
            monthly_service_usage (MonthlyServiceUsage):
            daily_service_usages (list[DailyServiceUsages]):
            total_usage_credits_usd_before_volume_discount (float):  Example: 0.786143673840067.
            total_usage_credits_usd_after_volume_discount (float):  Example: 0.786143673840067.
     """

    usage_cycle: UsageCycle
    monthly_service_usage: MonthlyServiceUsage
    daily_service_usages: list[DailyServiceUsages]
    total_usage_credits_usd_before_volume_discount: float
    total_usage_credits_usd_after_volume_discount: float
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.monthly_service_usage import MonthlyServiceUsage
        from ..models.usage_cycle import UsageCycle
        from ..models.daily_service_usages import DailyServiceUsages
        usage_cycle = self.usage_cycle.to_dict()

        monthly_service_usage = self.monthly_service_usage.to_dict()

        daily_service_usages = []
        for daily_service_usages_item_data in self.daily_service_usages:
            daily_service_usages_item = daily_service_usages_item_data.to_dict()
            daily_service_usages.append(daily_service_usages_item)



        total_usage_credits_usd_before_volume_discount = self.total_usage_credits_usd_before_volume_discount

        total_usage_credits_usd_after_volume_discount = self.total_usage_credits_usd_after_volume_discount


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "usageCycle": usage_cycle,
            "monthlyServiceUsage": monthly_service_usage,
            "dailyServiceUsages": daily_service_usages,
            "totalUsageCreditsUsdBeforeVolumeDiscount": total_usage_credits_usd_before_volume_discount,
            "totalUsageCreditsUsdAfterVolumeDiscount": total_usage_credits_usd_after_volume_discount,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.monthly_service_usage import MonthlyServiceUsage
        from ..models.usage_cycle import UsageCycle
        from ..models.daily_service_usages import DailyServiceUsages
        d = dict(src_dict)
        usage_cycle = UsageCycle.from_dict(d.pop("usageCycle"))




        monthly_service_usage = MonthlyServiceUsage.from_dict(d.pop("monthlyServiceUsage"))




        daily_service_usages = []
        _daily_service_usages = d.pop("dailyServiceUsages")
        for daily_service_usages_item_data in (_daily_service_usages):
            daily_service_usages_item = DailyServiceUsages.from_dict(daily_service_usages_item_data)



            daily_service_usages.append(daily_service_usages_item)


        total_usage_credits_usd_before_volume_discount = d.pop("totalUsageCreditsUsdBeforeVolumeDiscount")

        total_usage_credits_usd_after_volume_discount = d.pop("totalUsageCreditsUsdAfterVolumeDiscount")

        monthly_usage = cls(
            usage_cycle=usage_cycle,
            monthly_service_usage=monthly_service_usage,
            daily_service_usages=daily_service_usages,
            total_usage_credits_usd_before_volume_discount=total_usage_credits_usd_before_volume_discount,
            total_usage_credits_usd_after_volume_discount=total_usage_credits_usd_after_volume_discount,
        )


        monthly_usage.additional_properties = d
        return monthly_usage

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
