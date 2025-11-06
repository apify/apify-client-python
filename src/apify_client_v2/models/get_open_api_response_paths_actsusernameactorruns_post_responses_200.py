from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.get_open_api_response_paths_actsusernameactorruns_post_responses_200_content import GetOpenApiResponsePathsActsusernameactorrunsPostResponses200Content





T = TypeVar("T", bound="GetOpenApiResponsePathsActsusernameactorrunsPostResponses200")



@_attrs_define
class GetOpenApiResponsePathsActsusernameactorrunsPostResponses200:
    """ 
        Attributes:
            description (str | Unset):  Example: OK.
            content (GetOpenApiResponsePathsActsusernameactorrunsPostResponses200Content | Unset):
     """

    description: str | Unset = UNSET
    content: GetOpenApiResponsePathsActsusernameactorrunsPostResponses200Content | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.get_open_api_response_paths_actsusernameactorruns_post_responses_200_content import GetOpenApiResponsePathsActsusernameactorrunsPostResponses200Content
        description = self.description

        content: dict[str, Any] | Unset = UNSET
        if not isinstance(self.content, Unset):
            content = self.content.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if description is not UNSET:
            field_dict["description"] = description
        if content is not UNSET:
            field_dict["content"] = content

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_open_api_response_paths_actsusernameactorruns_post_responses_200_content import GetOpenApiResponsePathsActsusernameactorrunsPostResponses200Content
        d = dict(src_dict)
        description = d.pop("description", UNSET)

        _content = d.pop("content", UNSET)
        content: GetOpenApiResponsePathsActsusernameactorrunsPostResponses200Content | Unset
        if isinstance(_content,  Unset):
            content = UNSET
        else:
            content = GetOpenApiResponsePathsActsusernameactorrunsPostResponses200Content.from_dict(_content)




        get_open_api_response_paths_actsusernameactorruns_post_responses_200 = cls(
            description=description,
            content=content,
        )


        get_open_api_response_paths_actsusernameactorruns_post_responses_200.additional_properties = d
        return get_open_api_response_paths_actsusernameactorruns_post_responses_200

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
