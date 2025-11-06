from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.get_open_api_response_components_schemas_runs_response_schema_properties_data_properties import GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataProperties





T = TypeVar("T", bound="GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesData")



@_attrs_define
class GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesData:
    """ 
        Attributes:
            type_ (str | Unset):  Example: object.
            properties (GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataProperties | Unset):
     """

    type_: str | Unset = UNSET
    properties: GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataProperties | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.get_open_api_response_components_schemas_runs_response_schema_properties_data_properties import GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataProperties
        type_ = self.type_

        properties: dict[str, Any] | Unset = UNSET
        if not isinstance(self.properties, Unset):
            properties = self.properties.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if type_ is not UNSET:
            field_dict["type"] = type_
        if properties is not UNSET:
            field_dict["properties"] = properties

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_open_api_response_components_schemas_runs_response_schema_properties_data_properties import GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataProperties
        d = dict(src_dict)
        type_ = d.pop("type", UNSET)

        _properties = d.pop("properties", UNSET)
        properties: GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataProperties | Unset
        if isinstance(_properties,  Unset):
            properties = UNSET
        else:
            properties = GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataProperties.from_dict(_properties)




        get_open_api_response_components_schemas_runs_response_schema_properties_data = cls(
            type_=type_,
            properties=properties,
        )


        get_open_api_response_components_schemas_runs_response_schema_properties_data.additional_properties = d
        return get_open_api_response_components_schemas_runs_response_schema_properties_data

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
