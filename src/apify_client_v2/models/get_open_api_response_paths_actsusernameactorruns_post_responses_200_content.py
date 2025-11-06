from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.get_open_api_response_paths_actsusernameactorruns_post_responses_200_content_applicationjson import GetOpenApiResponsePathsActsusernameactorrunsPostResponses200ContentApplicationjson





T = TypeVar("T", bound="GetOpenApiResponsePathsActsusernameactorrunsPostResponses200Content")



@_attrs_define
class GetOpenApiResponsePathsActsusernameactorrunsPostResponses200Content:
    """ 
        Attributes:
            applicationjson (GetOpenApiResponsePathsActsusernameactorrunsPostResponses200ContentApplicationjson | Unset):
     """

    applicationjson: GetOpenApiResponsePathsActsusernameactorrunsPostResponses200ContentApplicationjson | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.get_open_api_response_paths_actsusernameactorruns_post_responses_200_content_applicationjson import GetOpenApiResponsePathsActsusernameactorrunsPostResponses200ContentApplicationjson
        applicationjson: dict[str, Any] | Unset = UNSET
        if not isinstance(self.applicationjson, Unset):
            applicationjson = self.applicationjson.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if applicationjson is not UNSET:
            field_dict["application/json"] = applicationjson

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_open_api_response_paths_actsusernameactorruns_post_responses_200_content_applicationjson import GetOpenApiResponsePathsActsusernameactorrunsPostResponses200ContentApplicationjson
        d = dict(src_dict)
        _applicationjson = d.pop("application/json", UNSET)
        applicationjson: GetOpenApiResponsePathsActsusernameactorrunsPostResponses200ContentApplicationjson | Unset
        if isinstance(_applicationjson,  Unset):
            applicationjson = UNSET
        else:
            applicationjson = GetOpenApiResponsePathsActsusernameactorrunsPostResponses200ContentApplicationjson.from_dict(_applicationjson)




        get_open_api_response_paths_actsusernameactorruns_post_responses_200_content = cls(
            applicationjson=applicationjson,
        )


        get_open_api_response_paths_actsusernameactorruns_post_responses_200_content.additional_properties = d
        return get_open_api_response_paths_actsusernameactorruns_post_responses_200_content

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
