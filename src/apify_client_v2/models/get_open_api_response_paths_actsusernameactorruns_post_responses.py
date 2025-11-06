from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.get_open_api_response_paths_actsusernameactorruns_post_responses_200 import GetOpenApiResponsePathsActsusernameactorrunsPostResponses200





T = TypeVar("T", bound="GetOpenApiResponsePathsActsusernameactorrunsPostResponses")



@_attrs_define
class GetOpenApiResponsePathsActsusernameactorrunsPostResponses:
    """ 
        Attributes:
            field_200 (GetOpenApiResponsePathsActsusernameactorrunsPostResponses200 | Unset):
     """

    field_200: GetOpenApiResponsePathsActsusernameactorrunsPostResponses200 | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.get_open_api_response_paths_actsusernameactorruns_post_responses_200 import GetOpenApiResponsePathsActsusernameactorrunsPostResponses200
        field_200: dict[str, Any] | Unset = UNSET
        if not isinstance(self.field_200, Unset):
            field_200 = self.field_200.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if field_200 is not UNSET:
            field_dict["200"] = field_200

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_open_api_response_paths_actsusernameactorruns_post_responses_200 import GetOpenApiResponsePathsActsusernameactorrunsPostResponses200
        d = dict(src_dict)
        _field_200 = d.pop("200", UNSET)
        field_200: GetOpenApiResponsePathsActsusernameactorrunsPostResponses200 | Unset
        if isinstance(_field_200,  Unset):
            field_200 = UNSET
        else:
            field_200 = GetOpenApiResponsePathsActsusernameactorrunsPostResponses200.from_dict(_field_200)




        get_open_api_response_paths_actsusernameactorruns_post_responses = cls(
            field_200=field_200,
        )


        get_open_api_response_paths_actsusernameactorruns_post_responses.additional_properties = d
        return get_open_api_response_paths_actsusernameactorruns_post_responses

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
