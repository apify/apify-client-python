from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset







T = TypeVar("T", bound="Current")



@_attrs_define
class Current:
    """ 
        Attributes:
            monthly_usage_usd (float):  Example: 43.
            monthly_actor_compute_units (float):  Example: 500.784475.
            monthly_external_data_transfer_gbytes (float):  Example: 3.00861903931946.
            monthly_proxy_serps (float):  Example: 34.
            monthly_residential_proxy_gbytes (float):  Example: 0.4.
            actor_memory_gbytes (float):  Example: 8.
            actor_count (float):  Example: 31.
            actor_task_count (float):  Example: 130.
            active_actor_job_count (float):
            team_account_seat_count (float):  Example: 5.
     """

    monthly_usage_usd: float
    monthly_actor_compute_units: float
    monthly_external_data_transfer_gbytes: float
    monthly_proxy_serps: float
    monthly_residential_proxy_gbytes: float
    actor_memory_gbytes: float
    actor_count: float
    actor_task_count: float
    active_actor_job_count: float
    team_account_seat_count: float
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        monthly_usage_usd = self.monthly_usage_usd

        monthly_actor_compute_units = self.monthly_actor_compute_units

        monthly_external_data_transfer_gbytes = self.monthly_external_data_transfer_gbytes

        monthly_proxy_serps = self.monthly_proxy_serps

        monthly_residential_proxy_gbytes = self.monthly_residential_proxy_gbytes

        actor_memory_gbytes = self.actor_memory_gbytes

        actor_count = self.actor_count

        actor_task_count = self.actor_task_count

        active_actor_job_count = self.active_actor_job_count

        team_account_seat_count = self.team_account_seat_count


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "monthlyUsageUsd": monthly_usage_usd,
            "monthlyActorComputeUnits": monthly_actor_compute_units,
            "monthlyExternalDataTransferGbytes": monthly_external_data_transfer_gbytes,
            "monthlyProxySerps": monthly_proxy_serps,
            "monthlyResidentialProxyGbytes": monthly_residential_proxy_gbytes,
            "actorMemoryGbytes": actor_memory_gbytes,
            "actorCount": actor_count,
            "actorTaskCount": actor_task_count,
            "activeActorJobCount": active_actor_job_count,
            "teamAccountSeatCount": team_account_seat_count,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        monthly_usage_usd = d.pop("monthlyUsageUsd")

        monthly_actor_compute_units = d.pop("monthlyActorComputeUnits")

        monthly_external_data_transfer_gbytes = d.pop("monthlyExternalDataTransferGbytes")

        monthly_proxy_serps = d.pop("monthlyProxySerps")

        monthly_residential_proxy_gbytes = d.pop("monthlyResidentialProxyGbytes")

        actor_memory_gbytes = d.pop("actorMemoryGbytes")

        actor_count = d.pop("actorCount")

        actor_task_count = d.pop("actorTaskCount")

        active_actor_job_count = d.pop("activeActorJobCount")

        team_account_seat_count = d.pop("teamAccountSeatCount")

        current = cls(
            monthly_usage_usd=monthly_usage_usd,
            monthly_actor_compute_units=monthly_actor_compute_units,
            monthly_external_data_transfer_gbytes=monthly_external_data_transfer_gbytes,
            monthly_proxy_serps=monthly_proxy_serps,
            monthly_residential_proxy_gbytes=monthly_residential_proxy_gbytes,
            actor_memory_gbytes=actor_memory_gbytes,
            actor_count=actor_count,
            actor_task_count=actor_task_count,
            active_actor_job_count=active_actor_job_count,
            team_account_seat_count=team_account_seat_count,
        )


        current.additional_properties = d
        return current

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
