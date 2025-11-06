from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset







T = TypeVar("T", bound="ActorStats")



@_attrs_define
class ActorStats:
    """ 
        Attributes:
            total_builds (float):  Example: 9.
            total_runs (float):  Example: 16.
            total_users (float):  Example: 6.
            total_users_7_days (float):  Example: 2.
            total_users_30_days (float):  Example: 6.
            total_users_90_days (float):  Example: 6.
            total_metamorphs (float):  Example: 2.
            last_run_started_at (str):  Example: 2019-07-08T14:01:05.546Z.
     """

    total_builds: float
    total_runs: float
    total_users: float
    total_users_7_days: float
    total_users_30_days: float
    total_users_90_days: float
    total_metamorphs: float
    last_run_started_at: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        total_builds = self.total_builds

        total_runs = self.total_runs

        total_users = self.total_users

        total_users_7_days = self.total_users_7_days

        total_users_30_days = self.total_users_30_days

        total_users_90_days = self.total_users_90_days

        total_metamorphs = self.total_metamorphs

        last_run_started_at = self.last_run_started_at


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "totalBuilds": total_builds,
            "totalRuns": total_runs,
            "totalUsers": total_users,
            "totalUsers7Days": total_users_7_days,
            "totalUsers30Days": total_users_30_days,
            "totalUsers90Days": total_users_90_days,
            "totalMetamorphs": total_metamorphs,
            "lastRunStartedAt": last_run_started_at,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        total_builds = d.pop("totalBuilds")

        total_runs = d.pop("totalRuns")

        total_users = d.pop("totalUsers")

        total_users_7_days = d.pop("totalUsers7Days")

        total_users_30_days = d.pop("totalUsers30Days")

        total_users_90_days = d.pop("totalUsers90Days")

        total_metamorphs = d.pop("totalMetamorphs")

        last_run_started_at = d.pop("lastRunStartedAt")

        actor_stats = cls(
            total_builds=total_builds,
            total_runs=total_runs,
            total_users=total_users,
            total_users_7_days=total_users_7_days,
            total_users_30_days=total_users_30_days,
            total_users_90_days=total_users_90_days,
            total_metamorphs=total_metamorphs,
            last_run_started_at=last_run_started_at,
        )


        actor_stats.additional_properties = d
        return actor_stats

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
