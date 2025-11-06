from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset






T = TypeVar("T", bound="GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesFinishedAt")



@_attrs_define
class GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesFinishedAt:
    """ 
        Attributes:
            type_ (str | Unset):  Example: string.
            format_ (str | Unset):  Example: date-time.
            example (str | Unset):  Example: 2025-01-08T00:00:00.000Z.
     """

    type_: str | Unset = UNSET
    format_: str | Unset = UNSET
    example: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        format_ = self.format_

        example = self.example


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if type_ is not UNSET:
            field_dict["type"] = type_
        if format_ is not UNSET:
            field_dict["format"] = format_
        if example is not UNSET:
            field_dict["example"] = example

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = d.pop("type", UNSET)

        format_ = d.pop("format", UNSET)

        example = d.pop("example", UNSET)

        get_open_api_response_components_schemas_runs_response_schema_properties_data_properties_finished_at = cls(
            type_=type_,
            format_=format_,
            example=example,
        )


        get_open_api_response_components_schemas_runs_response_schema_properties_data_properties_finished_at.additional_properties = d
        return get_open_api_response_components_schemas_runs_response_schema_properties_data_properties_finished_at

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
