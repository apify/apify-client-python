from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast






T = TypeVar("T", bound="BuildOptions")



@_attrs_define
class BuildOptions:
    """ 
        Attributes:
            use_cache (bool | None | Unset):
            beta_packages (bool | None | Unset):
            memory_mbytes (float | None | Unset):  Example: 1024.
            disk_mbytes (float | None | Unset):  Example: 2048.
     """

    use_cache: bool | None | Unset = UNSET
    beta_packages: bool | None | Unset = UNSET
    memory_mbytes: float | None | Unset = UNSET
    disk_mbytes: float | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        use_cache: bool | None | Unset
        if isinstance(self.use_cache, Unset):
            use_cache = UNSET
        else:
            use_cache = self.use_cache

        beta_packages: bool | None | Unset
        if isinstance(self.beta_packages, Unset):
            beta_packages = UNSET
        else:
            beta_packages = self.beta_packages

        memory_mbytes: float | None | Unset
        if isinstance(self.memory_mbytes, Unset):
            memory_mbytes = UNSET
        else:
            memory_mbytes = self.memory_mbytes

        disk_mbytes: float | None | Unset
        if isinstance(self.disk_mbytes, Unset):
            disk_mbytes = UNSET
        else:
            disk_mbytes = self.disk_mbytes


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if use_cache is not UNSET:
            field_dict["useCache"] = use_cache
        if beta_packages is not UNSET:
            field_dict["betaPackages"] = beta_packages
        if memory_mbytes is not UNSET:
            field_dict["memoryMbytes"] = memory_mbytes
        if disk_mbytes is not UNSET:
            field_dict["diskMbytes"] = disk_mbytes

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        def _parse_use_cache(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        use_cache = _parse_use_cache(d.pop("useCache", UNSET))


        def _parse_beta_packages(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        beta_packages = _parse_beta_packages(d.pop("betaPackages", UNSET))


        def _parse_memory_mbytes(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        memory_mbytes = _parse_memory_mbytes(d.pop("memoryMbytes", UNSET))


        def _parse_disk_mbytes(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        disk_mbytes = _parse_disk_mbytes(d.pop("diskMbytes", UNSET))


        build_options = cls(
            use_cache=use_cache,
            beta_packages=beta_packages,
            memory_mbytes=memory_mbytes,
            disk_mbytes=disk_mbytes,
        )


        build_options.additional_properties = d
        return build_options

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
