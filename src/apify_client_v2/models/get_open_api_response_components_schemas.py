from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.get_open_api_response_components_schemas_runs_response_schema import GetOpenApiResponseComponentsSchemasRunsResponseSchema
  from ..models.get_open_api_response_components_schemas_input_schema import GetOpenApiResponseComponentsSchemasInputSchema





T = TypeVar("T", bound="GetOpenApiResponseComponentsSchemas")



@_attrs_define
class GetOpenApiResponseComponentsSchemas:
    """ 
        Attributes:
            input_schema (GetOpenApiResponseComponentsSchemasInputSchema | Unset):
            runs_response_schema (GetOpenApiResponseComponentsSchemasRunsResponseSchema | Unset):
     """

    input_schema: GetOpenApiResponseComponentsSchemasInputSchema | Unset = UNSET
    runs_response_schema: GetOpenApiResponseComponentsSchemasRunsResponseSchema | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.get_open_api_response_components_schemas_runs_response_schema import GetOpenApiResponseComponentsSchemasRunsResponseSchema
        from ..models.get_open_api_response_components_schemas_input_schema import GetOpenApiResponseComponentsSchemasInputSchema
        input_schema: dict[str, Any] | Unset = UNSET
        if not isinstance(self.input_schema, Unset):
            input_schema = self.input_schema.to_dict()

        runs_response_schema: dict[str, Any] | Unset = UNSET
        if not isinstance(self.runs_response_schema, Unset):
            runs_response_schema = self.runs_response_schema.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if input_schema is not UNSET:
            field_dict["inputSchema"] = input_schema
        if runs_response_schema is not UNSET:
            field_dict["runsResponseSchema"] = runs_response_schema

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_open_api_response_components_schemas_runs_response_schema import GetOpenApiResponseComponentsSchemasRunsResponseSchema
        from ..models.get_open_api_response_components_schemas_input_schema import GetOpenApiResponseComponentsSchemasInputSchema
        d = dict(src_dict)
        _input_schema = d.pop("inputSchema", UNSET)
        input_schema: GetOpenApiResponseComponentsSchemasInputSchema | Unset
        if isinstance(_input_schema,  Unset):
            input_schema = UNSET
        else:
            input_schema = GetOpenApiResponseComponentsSchemasInputSchema.from_dict(_input_schema)




        _runs_response_schema = d.pop("runsResponseSchema", UNSET)
        runs_response_schema: GetOpenApiResponseComponentsSchemasRunsResponseSchema | Unset
        if isinstance(_runs_response_schema,  Unset):
            runs_response_schema = UNSET
        else:
            runs_response_schema = GetOpenApiResponseComponentsSchemasRunsResponseSchema.from_dict(_runs_response_schema)




        get_open_api_response_components_schemas = cls(
            input_schema=input_schema,
            runs_response_schema=runs_response_schema,
        )


        get_open_api_response_components_schemas.additional_properties = d
        return get_open_api_response_components_schemas

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
