from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.get_open_api_response_paths_actsusernameactorrun_sync_get_dataset_items_post_parameters_item_schema import GetOpenApiResponsePathsActsusernameactorrunSyncGetDatasetItemsPostParametersItemSchema





T = TypeVar("T", bound="GetOpenApiResponsePathsActsusernameactorrunSyncGetDatasetItemsPostParametersItem")



@_attrs_define
class GetOpenApiResponsePathsActsusernameactorrunSyncGetDatasetItemsPostParametersItem:
    """ 
        Attributes:
            name (str | Unset):  Example: token.
            in_ (str | Unset):  Example: query.
            required (bool | Unset):  Example: True.
            schema (GetOpenApiResponsePathsActsusernameactorrunSyncGetDatasetItemsPostParametersItemSchema | Unset):
            description (str | Unset):  Example: Enter your Apify token here.
     """

    name: str | Unset = UNSET
    in_: str | Unset = UNSET
    required: bool | Unset = UNSET
    schema: GetOpenApiResponsePathsActsusernameactorrunSyncGetDatasetItemsPostParametersItemSchema | Unset = UNSET
    description: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.get_open_api_response_paths_actsusernameactorrun_sync_get_dataset_items_post_parameters_item_schema import GetOpenApiResponsePathsActsusernameactorrunSyncGetDatasetItemsPostParametersItemSchema
        name = self.name

        in_ = self.in_

        required = self.required

        schema: dict[str, Any] | Unset = UNSET
        if not isinstance(self.schema, Unset):
            schema = self.schema.to_dict()

        description = self.description


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if name is not UNSET:
            field_dict["name"] = name
        if in_ is not UNSET:
            field_dict["in"] = in_
        if required is not UNSET:
            field_dict["required"] = required
        if schema is not UNSET:
            field_dict["schema"] = schema
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_open_api_response_paths_actsusernameactorrun_sync_get_dataset_items_post_parameters_item_schema import GetOpenApiResponsePathsActsusernameactorrunSyncGetDatasetItemsPostParametersItemSchema
        d = dict(src_dict)
        name = d.pop("name", UNSET)

        in_ = d.pop("in", UNSET)

        required = d.pop("required", UNSET)

        _schema = d.pop("schema", UNSET)
        schema: GetOpenApiResponsePathsActsusernameactorrunSyncGetDatasetItemsPostParametersItemSchema | Unset
        if isinstance(_schema,  Unset):
            schema = UNSET
        else:
            schema = GetOpenApiResponsePathsActsusernameactorrunSyncGetDatasetItemsPostParametersItemSchema.from_dict(_schema)




        description = d.pop("description", UNSET)

        get_open_api_response_paths_actsusernameactorrun_sync_get_dataset_items_post_parameters_item = cls(
            name=name,
            in_=in_,
            required=required,
            schema=schema,
            description=description,
        )


        get_open_api_response_paths_actsusernameactorrun_sync_get_dataset_items_post_parameters_item.additional_properties = d
        return get_open_api_response_paths_actsusernameactorrun_sync_get_dataset_items_post_parameters_item

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
