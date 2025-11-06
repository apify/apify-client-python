from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset






T = TypeVar("T", bound="GetOpenApiResponsePathsActsusernameactorrunsPostResponses200ContentApplicationjsonSchema")



@_attrs_define
class GetOpenApiResponsePathsActsusernameactorrunsPostResponses200ContentApplicationjsonSchema:
    """ 
        Attributes:
            ref (str | Unset):  Example: #/components/schemas/runsResponseSchema.
     """

    ref: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        ref = self.ref


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if ref is not UNSET:
            field_dict["$ref"] = ref

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        ref = d.pop("$ref", UNSET)

        get_open_api_response_paths_actsusernameactorruns_post_responses_200_content_applicationjson_schema = cls(
            ref=ref,
        )


        get_open_api_response_paths_actsusernameactorruns_post_responses_200_content_applicationjson_schema.additional_properties = d
        return get_open_api_response_paths_actsusernameactorruns_post_responses_200_content_applicationjson_schema

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
