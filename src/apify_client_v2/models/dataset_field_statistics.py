from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast






T = TypeVar("T", bound="DatasetFieldStatistics")



@_attrs_define
class DatasetFieldStatistics:
    """ 
        Attributes:
            min_ (float | None | Unset): Minimum value of the field. For numbers, this is calculated directly. For strings,
                this is the length of the shortest string. For arrays, this is the length of the shortest array. For objects,
                this is the number of keys in the smallest object.
            max_ (float | None | Unset): Maximum value of the field. For numbers, this is calculated directly. For strings,
                this is the length of the longest string. For arrays, this is the length of the longest array. For objects, this
                is the number of keys in the largest object.
            null_count (float | None | Unset): How many items in the dataset have a null value for this field.
            empty_count (float | None | Unset): How many items in the dataset are `undefined`, meaning that for example
                empty string is not considered empty.
     """

    min_: float | None | Unset = UNSET
    max_: float | None | Unset = UNSET
    null_count: float | None | Unset = UNSET
    empty_count: float | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        min_: float | None | Unset
        if isinstance(self.min_, Unset):
            min_ = UNSET
        else:
            min_ = self.min_

        max_: float | None | Unset
        if isinstance(self.max_, Unset):
            max_ = UNSET
        else:
            max_ = self.max_

        null_count: float | None | Unset
        if isinstance(self.null_count, Unset):
            null_count = UNSET
        else:
            null_count = self.null_count

        empty_count: float | None | Unset
        if isinstance(self.empty_count, Unset):
            empty_count = UNSET
        else:
            empty_count = self.empty_count


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if min_ is not UNSET:
            field_dict["min"] = min_
        if max_ is not UNSET:
            field_dict["max"] = max_
        if null_count is not UNSET:
            field_dict["nullCount"] = null_count
        if empty_count is not UNSET:
            field_dict["emptyCount"] = empty_count

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        def _parse_min_(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        min_ = _parse_min_(d.pop("min", UNSET))


        def _parse_max_(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        max_ = _parse_max_(d.pop("max", UNSET))


        def _parse_null_count(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        null_count = _parse_null_count(d.pop("nullCount", UNSET))


        def _parse_empty_count(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        empty_count = _parse_empty_count(d.pop("emptyCount", UNSET))


        dataset_field_statistics = cls(
            min_=min_,
            max_=max_,
            null_count=null_count,
            empty_count=empty_count,
        )


        dataset_field_statistics.additional_properties = d
        return dataset_field_statistics

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
