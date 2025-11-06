from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast






T = TypeVar("T", bound="TaggedBuildsLatestType1")



@_attrs_define
class TaggedBuildsLatestType1:
    """ 
        Attributes:
            build_id (None | str | Unset):  Example: z2EryhbfhgSyqj6Hn.
            build_number (None | str | Unset):  Example: 0.0.2.
            finished_at (None | str | Unset):  Example: 2019-06-10T11:15:49.286Z.
     """

    build_id: None | str | Unset = UNSET
    build_number: None | str | Unset = UNSET
    finished_at: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        build_id: None | str | Unset
        if isinstance(self.build_id, Unset):
            build_id = UNSET
        else:
            build_id = self.build_id

        build_number: None | str | Unset
        if isinstance(self.build_number, Unset):
            build_number = UNSET
        else:
            build_number = self.build_number

        finished_at: None | str | Unset
        if isinstance(self.finished_at, Unset):
            finished_at = UNSET
        else:
            finished_at = self.finished_at


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if build_id is not UNSET:
            field_dict["buildId"] = build_id
        if build_number is not UNSET:
            field_dict["buildNumber"] = build_number
        if finished_at is not UNSET:
            field_dict["finishedAt"] = finished_at

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        def _parse_build_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        build_id = _parse_build_id(d.pop("buildId", UNSET))


        def _parse_build_number(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        build_number = _parse_build_number(d.pop("buildNumber", UNSET))


        def _parse_finished_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        finished_at = _parse_finished_at(d.pop("finishedAt", UNSET))


        tagged_builds_latest_type_1 = cls(
            build_id=build_id,
            build_number=build_number,
            finished_at=finished_at,
        )


        tagged_builds_latest_type_1.additional_properties = d
        return tagged_builds_latest_type_1

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
