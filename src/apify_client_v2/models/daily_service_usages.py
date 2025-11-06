from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
  from ..models.service_usage import ServiceUsage





T = TypeVar("T", bound="DailyServiceUsages")



@_attrs_define
class DailyServiceUsages:
    """ 
        Attributes:
            date (str):  Example: 2022-10-02T00:00:00.000Z.
            service_usage (ServiceUsage):  Example: {'SERVICE_USAGE_ITEM': {'quantity': 60, 'baseAmountUsd':
                0.00030000000000000003}}.
            total_usage_credits_usd (float):  Example: 0.0474385791970591.
     """

    date: str
    service_usage: ServiceUsage
    total_usage_credits_usd: float
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.service_usage import ServiceUsage
        date = self.date

        service_usage = self.service_usage.to_dict()

        total_usage_credits_usd = self.total_usage_credits_usd


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "date": date,
            "serviceUsage": service_usage,
            "totalUsageCreditsUsd": total_usage_credits_usd,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.service_usage import ServiceUsage
        d = dict(src_dict)
        date = d.pop("date")

        service_usage = ServiceUsage.from_dict(d.pop("serviceUsage"))




        total_usage_credits_usd = d.pop("totalUsageCreditsUsd")

        daily_service_usages = cls(
            date=date,
            service_usage=service_usage,
            total_usage_credits_usd=total_usage_credits_usd,
        )


        daily_service_usages.additional_properties = d
        return daily_service_usages

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
