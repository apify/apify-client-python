from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.get_open_api_response_components_schemas_runs_response_schema_properties_data_properties_meta_properties_user_agent import GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesMetaPropertiesUserAgent
  from ..models.get_open_api_response_components_schemas_runs_response_schema_properties_data_properties_meta_properties_origin import GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesMetaPropertiesOrigin





T = TypeVar("T", bound="GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesMetaProperties")



@_attrs_define
class GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesMetaProperties:
    """ 
        Attributes:
            origin (GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesMetaPropertiesOrigin |
                Unset):
            user_agent (GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesMetaPropertiesUserAgent
                | Unset):
     """

    origin: GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesMetaPropertiesOrigin | Unset = UNSET
    user_agent: GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesMetaPropertiesUserAgent | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.get_open_api_response_components_schemas_runs_response_schema_properties_data_properties_meta_properties_user_agent import GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesMetaPropertiesUserAgent
        from ..models.get_open_api_response_components_schemas_runs_response_schema_properties_data_properties_meta_properties_origin import GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesMetaPropertiesOrigin
        origin: dict[str, Any] | Unset = UNSET
        if not isinstance(self.origin, Unset):
            origin = self.origin.to_dict()

        user_agent: dict[str, Any] | Unset = UNSET
        if not isinstance(self.user_agent, Unset):
            user_agent = self.user_agent.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if origin is not UNSET:
            field_dict["origin"] = origin
        if user_agent is not UNSET:
            field_dict["userAgent"] = user_agent

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_open_api_response_components_schemas_runs_response_schema_properties_data_properties_meta_properties_user_agent import GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesMetaPropertiesUserAgent
        from ..models.get_open_api_response_components_schemas_runs_response_schema_properties_data_properties_meta_properties_origin import GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesMetaPropertiesOrigin
        d = dict(src_dict)
        _origin = d.pop("origin", UNSET)
        origin: GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesMetaPropertiesOrigin | Unset
        if isinstance(_origin,  Unset):
            origin = UNSET
        else:
            origin = GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesMetaPropertiesOrigin.from_dict(_origin)




        _user_agent = d.pop("userAgent", UNSET)
        user_agent: GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesMetaPropertiesUserAgent | Unset
        if isinstance(_user_agent,  Unset):
            user_agent = UNSET
        else:
            user_agent = GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesMetaPropertiesUserAgent.from_dict(_user_agent)




        get_open_api_response_components_schemas_runs_response_schema_properties_data_properties_meta_properties = cls(
            origin=origin,
            user_agent=user_agent,
        )


        get_open_api_response_components_schemas_runs_response_schema_properties_data_properties_meta_properties.additional_properties = d
        return get_open_api_response_components_schemas_runs_response_schema_properties_data_properties_meta_properties

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
