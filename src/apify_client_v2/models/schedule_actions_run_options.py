from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast






T = TypeVar("T", bound="ScheduleActionsRunOptions")



@_attrs_define
class ScheduleActionsRunOptions:
    """ 
        Attributes:
            build (None | str | Unset):  Example: latest.
            timeout_secs (float | None | Unset):  Example: 60.
            memory_mbytes (float | None | Unset):  Example: 1024.
            restart_on_error (bool | None | Unset):
     """

    build: None | str | Unset = UNSET
    timeout_secs: float | None | Unset = UNSET
    memory_mbytes: float | None | Unset = UNSET
    restart_on_error: bool | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        build: None | str | Unset
        if isinstance(self.build, Unset):
            build = UNSET
        else:
            build = self.build

        timeout_secs: float | None | Unset
        if isinstance(self.timeout_secs, Unset):
            timeout_secs = UNSET
        else:
            timeout_secs = self.timeout_secs

        memory_mbytes: float | None | Unset
        if isinstance(self.memory_mbytes, Unset):
            memory_mbytes = UNSET
        else:
            memory_mbytes = self.memory_mbytes

        restart_on_error: bool | None | Unset
        if isinstance(self.restart_on_error, Unset):
            restart_on_error = UNSET
        else:
            restart_on_error = self.restart_on_error


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if build is not UNSET:
            field_dict["build"] = build
        if timeout_secs is not UNSET:
            field_dict["timeoutSecs"] = timeout_secs
        if memory_mbytes is not UNSET:
            field_dict["memoryMbytes"] = memory_mbytes
        if restart_on_error is not UNSET:
            field_dict["restartOnError"] = restart_on_error

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        def _parse_build(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        build = _parse_build(d.pop("build", UNSET))


        def _parse_timeout_secs(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        timeout_secs = _parse_timeout_secs(d.pop("timeoutSecs", UNSET))


        def _parse_memory_mbytes(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        memory_mbytes = _parse_memory_mbytes(d.pop("memoryMbytes", UNSET))


        def _parse_restart_on_error(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        restart_on_error = _parse_restart_on_error(d.pop("restartOnError", UNSET))


        schedule_actions_run_options = cls(
            build=build,
            timeout_secs=timeout_secs,
            memory_mbytes=memory_mbytes,
            restart_on_error=restart_on_error,
        )


        schedule_actions_run_options.additional_properties = d
        return schedule_actions_run_options

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
