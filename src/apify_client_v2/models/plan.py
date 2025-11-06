from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
  from ..models.available_proxy_groups import AvailableProxyGroups





T = TypeVar("T", bound="Plan")



@_attrs_define
class Plan:
    """ 
        Attributes:
            id (str):  Example: Personal.
            description (str):  Example: Cost-effective plan for freelancers, developers and students..
            is_enabled (bool):  Example: True.
            monthly_base_price_usd (float):  Example: 49.
            monthly_usage_credits_usd (float):  Example: 49.
            usage_discount_percent (float):
            enabled_platform_features (list[list[Any]]):  Example: [['ACTORS'], ['STORAGE'], ['PROXY_SERPS'], ['SCHEDULER'],
                ['WEBHOOKS']].
            max_monthly_usage_usd (float):  Example: 9999.
            max_actor_memory_gbytes (float):  Example: 32.
            max_monthly_actor_compute_units (float):  Example: 1000.
            max_monthly_residential_proxy_gbytes (float):  Example: 10.
            max_monthly_proxy_serps (float):  Example: 30000.
            max_monthly_external_data_transfer_gbytes (float):  Example: 1000.
            max_actor_count (float):  Example: 100.
            max_actor_task_count (float):  Example: 1000.
            data_retention_days (float):  Example: 14.
            available_proxy_groups (AvailableProxyGroups):
            team_account_seat_count (float):  Example: 1.
            support_level (str):  Example: COMMUNITY.
            available_add_ons (list[str]):
     """

    id: str
    description: str
    is_enabled: bool
    monthly_base_price_usd: float
    monthly_usage_credits_usd: float
    usage_discount_percent: float
    enabled_platform_features: list[list[Any]]
    max_monthly_usage_usd: float
    max_actor_memory_gbytes: float
    max_monthly_actor_compute_units: float
    max_monthly_residential_proxy_gbytes: float
    max_monthly_proxy_serps: float
    max_monthly_external_data_transfer_gbytes: float
    max_actor_count: float
    max_actor_task_count: float
    data_retention_days: float
    available_proxy_groups: AvailableProxyGroups
    team_account_seat_count: float
    support_level: str
    available_add_ons: list[str]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.available_proxy_groups import AvailableProxyGroups
        id = self.id

        description = self.description

        is_enabled = self.is_enabled

        monthly_base_price_usd = self.monthly_base_price_usd

        monthly_usage_credits_usd = self.monthly_usage_credits_usd

        usage_discount_percent = self.usage_discount_percent

        enabled_platform_features = []
        for enabled_platform_features_item_data in self.enabled_platform_features:
            enabled_platform_features_item = enabled_platform_features_item_data


            enabled_platform_features.append(enabled_platform_features_item)



        max_monthly_usage_usd = self.max_monthly_usage_usd

        max_actor_memory_gbytes = self.max_actor_memory_gbytes

        max_monthly_actor_compute_units = self.max_monthly_actor_compute_units

        max_monthly_residential_proxy_gbytes = self.max_monthly_residential_proxy_gbytes

        max_monthly_proxy_serps = self.max_monthly_proxy_serps

        max_monthly_external_data_transfer_gbytes = self.max_monthly_external_data_transfer_gbytes

        max_actor_count = self.max_actor_count

        max_actor_task_count = self.max_actor_task_count

        data_retention_days = self.data_retention_days

        available_proxy_groups = self.available_proxy_groups.to_dict()

        team_account_seat_count = self.team_account_seat_count

        support_level = self.support_level

        available_add_ons = self.available_add_ons




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "description": description,
            "isEnabled": is_enabled,
            "monthlyBasePriceUsd": monthly_base_price_usd,
            "monthlyUsageCreditsUsd": monthly_usage_credits_usd,
            "usageDiscountPercent": usage_discount_percent,
            "enabledPlatformFeatures": enabled_platform_features,
            "maxMonthlyUsageUsd": max_monthly_usage_usd,
            "maxActorMemoryGbytes": max_actor_memory_gbytes,
            "maxMonthlyActorComputeUnits": max_monthly_actor_compute_units,
            "maxMonthlyResidentialProxyGbytes": max_monthly_residential_proxy_gbytes,
            "maxMonthlyProxySerps": max_monthly_proxy_serps,
            "maxMonthlyExternalDataTransferGbytes": max_monthly_external_data_transfer_gbytes,
            "maxActorCount": max_actor_count,
            "maxActorTaskCount": max_actor_task_count,
            "dataRetentionDays": data_retention_days,
            "availableProxyGroups": available_proxy_groups,
            "teamAccountSeatCount": team_account_seat_count,
            "supportLevel": support_level,
            "availableAddOns": available_add_ons,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.available_proxy_groups import AvailableProxyGroups
        d = dict(src_dict)
        id = d.pop("id")

        description = d.pop("description")

        is_enabled = d.pop("isEnabled")

        monthly_base_price_usd = d.pop("monthlyBasePriceUsd")

        monthly_usage_credits_usd = d.pop("monthlyUsageCreditsUsd")

        usage_discount_percent = d.pop("usageDiscountPercent")

        enabled_platform_features = []
        _enabled_platform_features = d.pop("enabledPlatformFeatures")
        for enabled_platform_features_item_data in (_enabled_platform_features):
            enabled_platform_features_item = cast(list[Any], enabled_platform_features_item_data)

            enabled_platform_features.append(enabled_platform_features_item)


        max_monthly_usage_usd = d.pop("maxMonthlyUsageUsd")

        max_actor_memory_gbytes = d.pop("maxActorMemoryGbytes")

        max_monthly_actor_compute_units = d.pop("maxMonthlyActorComputeUnits")

        max_monthly_residential_proxy_gbytes = d.pop("maxMonthlyResidentialProxyGbytes")

        max_monthly_proxy_serps = d.pop("maxMonthlyProxySerps")

        max_monthly_external_data_transfer_gbytes = d.pop("maxMonthlyExternalDataTransferGbytes")

        max_actor_count = d.pop("maxActorCount")

        max_actor_task_count = d.pop("maxActorTaskCount")

        data_retention_days = d.pop("dataRetentionDays")

        available_proxy_groups = AvailableProxyGroups.from_dict(d.pop("availableProxyGroups"))




        team_account_seat_count = d.pop("teamAccountSeatCount")

        support_level = d.pop("supportLevel")

        available_add_ons = cast(list[str], d.pop("availableAddOns"))


        plan = cls(
            id=id,
            description=description,
            is_enabled=is_enabled,
            monthly_base_price_usd=monthly_base_price_usd,
            monthly_usage_credits_usd=monthly_usage_credits_usd,
            usage_discount_percent=usage_discount_percent,
            enabled_platform_features=enabled_platform_features,
            max_monthly_usage_usd=max_monthly_usage_usd,
            max_actor_memory_gbytes=max_actor_memory_gbytes,
            max_monthly_actor_compute_units=max_monthly_actor_compute_units,
            max_monthly_residential_proxy_gbytes=max_monthly_residential_proxy_gbytes,
            max_monthly_proxy_serps=max_monthly_proxy_serps,
            max_monthly_external_data_transfer_gbytes=max_monthly_external_data_transfer_gbytes,
            max_actor_count=max_actor_count,
            max_actor_task_count=max_actor_task_count,
            data_retention_days=data_retention_days,
            available_proxy_groups=available_proxy_groups,
            team_account_seat_count=team_account_seat_count,
            support_level=support_level,
            available_add_ons=available_add_ons,
        )


        plan.additional_properties = d
        return plan

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
