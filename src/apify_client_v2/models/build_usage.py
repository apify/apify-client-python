from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast






T = TypeVar("T", bound="BuildUsage")



@_attrs_define
class BuildUsage:
    """ 
        Attributes:
            actor_compute_units (float | None | Unset):  Example: 0.08.
     """

    actor_compute_units: float | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        actor_compute_units: float | None | Unset
        if isinstance(self.actor_compute_units, Unset):
            actor_compute_units = UNSET
        else:
            actor_compute_units = self.actor_compute_units


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if actor_compute_units is not UNSET:
            field_dict["ACTOR_COMPUTE_UNITS"] = actor_compute_units

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        def _parse_actor_compute_units(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        actor_compute_units = _parse_actor_compute_units(d.pop("ACTOR_COMPUTE_UNITS", UNSET))


        build_usage = cls(
            actor_compute_units=actor_compute_units,
        )


        build_usage.additional_properties = d
        return build_usage

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
