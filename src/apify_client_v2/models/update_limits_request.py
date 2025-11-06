from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset






T = TypeVar("T", bound="UpdateLimitsRequest")



@_attrs_define
class UpdateLimitsRequest:
    """ 
        Attributes:
            max_monthly_usage_usd (float | Unset): If your platform usage in the billing period exceeds the prepaid usage,
                you will be charged extra.
                Setting this property you can update your hard limit on monthly platform usage to prevent accidental overage or
                to limit the extra charges
                 Example: 300.
            data_retention_days (float | Unset): Apify securely stores your ten most recent Actor runs indefinitely,
                ensuring they are always accessible.
                Unnamed storages and other Actor runs are automatically deleted after the retention period.
                If you're subscribed, you can change it to keep data for longer or to limit your usage. [Lear
                more](https://docs.apify.com/platform/storage/usage#data-retention)
                 Example: 90.
     """

    max_monthly_usage_usd: float | Unset = UNSET
    data_retention_days: float | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        max_monthly_usage_usd = self.max_monthly_usage_usd

        data_retention_days = self.data_retention_days


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if max_monthly_usage_usd is not UNSET:
            field_dict["maxMonthlyUsageUsd"] = max_monthly_usage_usd
        if data_retention_days is not UNSET:
            field_dict["dataRetentionDays"] = data_retention_days

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        max_monthly_usage_usd = d.pop("maxMonthlyUsageUsd", UNSET)

        data_retention_days = d.pop("dataRetentionDays", UNSET)

        update_limits_request = cls(
            max_monthly_usage_usd=max_monthly_usage_usd,
            data_retention_days=data_retention_days,
        )


        update_limits_request.additional_properties = d
        return update_limits_request

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
