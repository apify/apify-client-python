from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset







T = TypeVar("T", bound="Limits")



@_attrs_define
class Limits:
    """ 
        Attributes:
            max_monthly_usage_usd (float):  Example: 300.
            max_monthly_actor_compute_units (float):  Example: 1000.
            max_monthly_external_data_transfer_gbytes (float):  Example: 7.
            max_monthly_proxy_serps (float):  Example: 50.
            max_monthly_residential_proxy_gbytes (float):  Example: 0.5.
            max_actor_memory_gbytes (float):  Example: 16.
            max_actor_count (float):  Example: 100.
            max_actor_task_count (float):  Example: 1000.
            max_concurrent_actor_jobs (float):  Example: 256.
            max_team_account_seat_count (float):  Example: 9.
            data_retention_days (float):  Example: 90.
     """

    max_monthly_usage_usd: float
    max_monthly_actor_compute_units: float
    max_monthly_external_data_transfer_gbytes: float
    max_monthly_proxy_serps: float
    max_monthly_residential_proxy_gbytes: float
    max_actor_memory_gbytes: float
    max_actor_count: float
    max_actor_task_count: float
    max_concurrent_actor_jobs: float
    max_team_account_seat_count: float
    data_retention_days: float
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        max_monthly_usage_usd = self.max_monthly_usage_usd

        max_monthly_actor_compute_units = self.max_monthly_actor_compute_units

        max_monthly_external_data_transfer_gbytes = self.max_monthly_external_data_transfer_gbytes

        max_monthly_proxy_serps = self.max_monthly_proxy_serps

        max_monthly_residential_proxy_gbytes = self.max_monthly_residential_proxy_gbytes

        max_actor_memory_gbytes = self.max_actor_memory_gbytes

        max_actor_count = self.max_actor_count

        max_actor_task_count = self.max_actor_task_count

        max_concurrent_actor_jobs = self.max_concurrent_actor_jobs

        max_team_account_seat_count = self.max_team_account_seat_count

        data_retention_days = self.data_retention_days


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "maxMonthlyUsageUsd": max_monthly_usage_usd,
            "maxMonthlyActorComputeUnits": max_monthly_actor_compute_units,
            "maxMonthlyExternalDataTransferGbytes": max_monthly_external_data_transfer_gbytes,
            "maxMonthlyProxySerps": max_monthly_proxy_serps,
            "maxMonthlyResidentialProxyGbytes": max_monthly_residential_proxy_gbytes,
            "maxActorMemoryGbytes": max_actor_memory_gbytes,
            "maxActorCount": max_actor_count,
            "maxActorTaskCount": max_actor_task_count,
            "maxConcurrentActorJobs": max_concurrent_actor_jobs,
            "maxTeamAccountSeatCount": max_team_account_seat_count,
            "dataRetentionDays": data_retention_days,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        max_monthly_usage_usd = d.pop("maxMonthlyUsageUsd")

        max_monthly_actor_compute_units = d.pop("maxMonthlyActorComputeUnits")

        max_monthly_external_data_transfer_gbytes = d.pop("maxMonthlyExternalDataTransferGbytes")

        max_monthly_proxy_serps = d.pop("maxMonthlyProxySerps")

        max_monthly_residential_proxy_gbytes = d.pop("maxMonthlyResidentialProxyGbytes")

        max_actor_memory_gbytes = d.pop("maxActorMemoryGbytes")

        max_actor_count = d.pop("maxActorCount")

        max_actor_task_count = d.pop("maxActorTaskCount")

        max_concurrent_actor_jobs = d.pop("maxConcurrentActorJobs")

        max_team_account_seat_count = d.pop("maxTeamAccountSeatCount")

        data_retention_days = d.pop("dataRetentionDays")

        limits = cls(
            max_monthly_usage_usd=max_monthly_usage_usd,
            max_monthly_actor_compute_units=max_monthly_actor_compute_units,
            max_monthly_external_data_transfer_gbytes=max_monthly_external_data_transfer_gbytes,
            max_monthly_proxy_serps=max_monthly_proxy_serps,
            max_monthly_residential_proxy_gbytes=max_monthly_residential_proxy_gbytes,
            max_actor_memory_gbytes=max_actor_memory_gbytes,
            max_actor_count=max_actor_count,
            max_actor_task_count=max_actor_task_count,
            max_concurrent_actor_jobs=max_concurrent_actor_jobs,
            max_team_account_seat_count=max_team_account_seat_count,
            data_retention_days=data_retention_days,
        )


        limits.additional_properties = d
        return limits

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
