from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset






T = TypeVar("T", bound="DefaultRunOptions")



@_attrs_define
class DefaultRunOptions:
    """ 
        Attributes:
            build (str):  Example: latest.
            timeout_secs (float):  Example: 3600.
            memory_mbytes (float):  Example: 2048.
            restart_on_error (bool | Unset):
     """

    build: str
    timeout_secs: float
    memory_mbytes: float
    restart_on_error: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        build = self.build

        timeout_secs = self.timeout_secs

        memory_mbytes = self.memory_mbytes

        restart_on_error = self.restart_on_error


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "build": build,
            "timeoutSecs": timeout_secs,
            "memoryMbytes": memory_mbytes,
        })
        if restart_on_error is not UNSET:
            field_dict["restartOnError"] = restart_on_error

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        build = d.pop("build")

        timeout_secs = d.pop("timeoutSecs")

        memory_mbytes = d.pop("memoryMbytes")

        restart_on_error = d.pop("restartOnError", UNSET)

        default_run_options = cls(
            build=build,
            timeout_secs=timeout_secs,
            memory_mbytes=memory_mbytes,
            restart_on_error=restart_on_error,
        )


        default_run_options.additional_properties = d
        return default_run_options

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
