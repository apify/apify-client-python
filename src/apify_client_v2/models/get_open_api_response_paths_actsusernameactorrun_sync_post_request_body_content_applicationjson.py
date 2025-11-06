from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.get_open_api_response_paths_actsusernameactorrun_sync_post_request_body_content_applicationjson_schema import GetOpenApiResponsePathsActsusernameactorrunSyncPostRequestBodyContentApplicationjsonSchema





T = TypeVar("T", bound="GetOpenApiResponsePathsActsusernameactorrunSyncPostRequestBodyContentApplicationjson")



@_attrs_define
class GetOpenApiResponsePathsActsusernameactorrunSyncPostRequestBodyContentApplicationjson:
    """ 
        Attributes:
            schema (GetOpenApiResponsePathsActsusernameactorrunSyncPostRequestBodyContentApplicationjsonSchema | Unset):
     """

    schema: GetOpenApiResponsePathsActsusernameactorrunSyncPostRequestBodyContentApplicationjsonSchema | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.get_open_api_response_paths_actsusernameactorrun_sync_post_request_body_content_applicationjson_schema import GetOpenApiResponsePathsActsusernameactorrunSyncPostRequestBodyContentApplicationjsonSchema
        schema: dict[str, Any] | Unset = UNSET
        if not isinstance(self.schema, Unset):
            schema = self.schema.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if schema is not UNSET:
            field_dict["schema"] = schema

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_open_api_response_paths_actsusernameactorrun_sync_post_request_body_content_applicationjson_schema import GetOpenApiResponsePathsActsusernameactorrunSyncPostRequestBodyContentApplicationjsonSchema
        d = dict(src_dict)
        _schema = d.pop("schema", UNSET)
        schema: GetOpenApiResponsePathsActsusernameactorrunSyncPostRequestBodyContentApplicationjsonSchema | Unset
        if isinstance(_schema,  Unset):
            schema = UNSET
        else:
            schema = GetOpenApiResponsePathsActsusernameactorrunSyncPostRequestBodyContentApplicationjsonSchema.from_dict(_schema)




        get_open_api_response_paths_actsusernameactorrun_sync_post_request_body_content_applicationjson = cls(
            schema=schema,
        )


        get_open_api_response_paths_actsusernameactorrun_sync_post_request_body_content_applicationjson.additional_properties = d
        return get_open_api_response_paths_actsusernameactorrun_sync_post_request_body_content_applicationjson

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
