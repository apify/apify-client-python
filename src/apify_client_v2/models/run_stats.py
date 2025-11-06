from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset






T = TypeVar("T", bound="RunStats")



@_attrs_define
class RunStats:
    """ 
        Attributes:
            restart_count (float):
            resurrect_count (float):  Example: 2.
            compute_units (float):  Example: 0.13804.
            input_body_len (float | Unset):  Example: 240.
            migration_count (float | Unset):
            mem_avg_bytes (float | Unset):  Example: 267874071.9.
            mem_max_bytes (float | Unset):  Example: 404713472.
            mem_current_bytes (float | Unset):
            cpu_avg_usage (float | Unset):  Example: 33.7532101107538.
            cpu_max_usage (float | Unset):  Example: 169.650735534941.
            cpu_current_usage (float | Unset):
            net_rx_bytes (float | Unset):  Example: 103508042.
            net_tx_bytes (float | Unset):  Example: 4854600.
            duration_millis (float | Unset):  Example: 248472.
            run_time_secs (float | Unset):  Example: 248.472.
            metamorph (float | Unset):
     """

    restart_count: float
    resurrect_count: float
    compute_units: float
    input_body_len: float | Unset = UNSET
    migration_count: float | Unset = UNSET
    mem_avg_bytes: float | Unset = UNSET
    mem_max_bytes: float | Unset = UNSET
    mem_current_bytes: float | Unset = UNSET
    cpu_avg_usage: float | Unset = UNSET
    cpu_max_usage: float | Unset = UNSET
    cpu_current_usage: float | Unset = UNSET
    net_rx_bytes: float | Unset = UNSET
    net_tx_bytes: float | Unset = UNSET
    duration_millis: float | Unset = UNSET
    run_time_secs: float | Unset = UNSET
    metamorph: float | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        restart_count = self.restart_count

        resurrect_count = self.resurrect_count

        compute_units = self.compute_units

        input_body_len = self.input_body_len

        migration_count = self.migration_count

        mem_avg_bytes = self.mem_avg_bytes

        mem_max_bytes = self.mem_max_bytes

        mem_current_bytes = self.mem_current_bytes

        cpu_avg_usage = self.cpu_avg_usage

        cpu_max_usage = self.cpu_max_usage

        cpu_current_usage = self.cpu_current_usage

        net_rx_bytes = self.net_rx_bytes

        net_tx_bytes = self.net_tx_bytes

        duration_millis = self.duration_millis

        run_time_secs = self.run_time_secs

        metamorph = self.metamorph


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "restartCount": restart_count,
            "resurrectCount": resurrect_count,
            "computeUnits": compute_units,
        })
        if input_body_len is not UNSET:
            field_dict["inputBodyLen"] = input_body_len
        if migration_count is not UNSET:
            field_dict["migrationCount"] = migration_count
        if mem_avg_bytes is not UNSET:
            field_dict["memAvgBytes"] = mem_avg_bytes
        if mem_max_bytes is not UNSET:
            field_dict["memMaxBytes"] = mem_max_bytes
        if mem_current_bytes is not UNSET:
            field_dict["memCurrentBytes"] = mem_current_bytes
        if cpu_avg_usage is not UNSET:
            field_dict["cpuAvgUsage"] = cpu_avg_usage
        if cpu_max_usage is not UNSET:
            field_dict["cpuMaxUsage"] = cpu_max_usage
        if cpu_current_usage is not UNSET:
            field_dict["cpuCurrentUsage"] = cpu_current_usage
        if net_rx_bytes is not UNSET:
            field_dict["netRxBytes"] = net_rx_bytes
        if net_tx_bytes is not UNSET:
            field_dict["netTxBytes"] = net_tx_bytes
        if duration_millis is not UNSET:
            field_dict["durationMillis"] = duration_millis
        if run_time_secs is not UNSET:
            field_dict["runTimeSecs"] = run_time_secs
        if metamorph is not UNSET:
            field_dict["metamorph"] = metamorph

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        restart_count = d.pop("restartCount")

        resurrect_count = d.pop("resurrectCount")

        compute_units = d.pop("computeUnits")

        input_body_len = d.pop("inputBodyLen", UNSET)

        migration_count = d.pop("migrationCount", UNSET)

        mem_avg_bytes = d.pop("memAvgBytes", UNSET)

        mem_max_bytes = d.pop("memMaxBytes", UNSET)

        mem_current_bytes = d.pop("memCurrentBytes", UNSET)

        cpu_avg_usage = d.pop("cpuAvgUsage", UNSET)

        cpu_max_usage = d.pop("cpuMaxUsage", UNSET)

        cpu_current_usage = d.pop("cpuCurrentUsage", UNSET)

        net_rx_bytes = d.pop("netRxBytes", UNSET)

        net_tx_bytes = d.pop("netTxBytes", UNSET)

        duration_millis = d.pop("durationMillis", UNSET)

        run_time_secs = d.pop("runTimeSecs", UNSET)

        metamorph = d.pop("metamorph", UNSET)

        run_stats = cls(
            restart_count=restart_count,
            resurrect_count=resurrect_count,
            compute_units=compute_units,
            input_body_len=input_body_len,
            migration_count=migration_count,
            mem_avg_bytes=mem_avg_bytes,
            mem_max_bytes=mem_max_bytes,
            mem_current_bytes=mem_current_bytes,
            cpu_avg_usage=cpu_avg_usage,
            cpu_max_usage=cpu_max_usage,
            cpu_current_usage=cpu_current_usage,
            net_rx_bytes=net_rx_bytes,
            net_tx_bytes=net_tx_bytes,
            duration_millis=duration_millis,
            run_time_secs=run_time_secs,
            metamorph=metamorph,
        )


        run_stats.additional_properties = d
        return run_stats

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
