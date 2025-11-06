from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.get_open_api_response_components_schemas import GetOpenApiResponseComponentsSchemas





T = TypeVar("T", bound="GetOpenApiResponseComponents")



@_attrs_define
class GetOpenApiResponseComponents:
    """ 
        Attributes:
            schemas (GetOpenApiResponseComponentsSchemas | Unset):
     """

    schemas: GetOpenApiResponseComponentsSchemas | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.get_open_api_response_components_schemas import GetOpenApiResponseComponentsSchemas
        schemas: dict[str, Any] | Unset = UNSET
        if not isinstance(self.schemas, Unset):
            schemas = self.schemas.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if schemas is not UNSET:
            field_dict["schemas"] = schemas

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_open_api_response_components_schemas import GetOpenApiResponseComponentsSchemas
        d = dict(src_dict)
        _schemas = d.pop("schemas", UNSET)
        schemas: GetOpenApiResponseComponentsSchemas | Unset
        if isinstance(_schemas,  Unset):
            schemas = UNSET
        else:
            schemas = GetOpenApiResponseComponentsSchemas.from_dict(_schemas)




        get_open_api_response_components = cls(
            schemas=schemas,
        )


        get_open_api_response_components.additional_properties = d
        return get_open_api_response_components

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
