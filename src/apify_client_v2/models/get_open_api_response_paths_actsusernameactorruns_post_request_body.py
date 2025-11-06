from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.get_open_api_response_paths_actsusernameactorruns_post_request_body_content import GetOpenApiResponsePathsActsusernameactorrunsPostRequestBodyContent





T = TypeVar("T", bound="GetOpenApiResponsePathsActsusernameactorrunsPostRequestBody")



@_attrs_define
class GetOpenApiResponsePathsActsusernameactorrunsPostRequestBody:
    """ 
        Attributes:
            required (bool | Unset):  Example: True.
            content (GetOpenApiResponsePathsActsusernameactorrunsPostRequestBodyContent | Unset):
     """

    required: bool | Unset = UNSET
    content: GetOpenApiResponsePathsActsusernameactorrunsPostRequestBodyContent | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.get_open_api_response_paths_actsusernameactorruns_post_request_body_content import GetOpenApiResponsePathsActsusernameactorrunsPostRequestBodyContent
        required = self.required

        content: dict[str, Any] | Unset = UNSET
        if not isinstance(self.content, Unset):
            content = self.content.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if required is not UNSET:
            field_dict["required"] = required
        if content is not UNSET:
            field_dict["content"] = content

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_open_api_response_paths_actsusernameactorruns_post_request_body_content import GetOpenApiResponsePathsActsusernameactorrunsPostRequestBodyContent
        d = dict(src_dict)
        required = d.pop("required", UNSET)

        _content = d.pop("content", UNSET)
        content: GetOpenApiResponsePathsActsusernameactorrunsPostRequestBodyContent | Unset
        if isinstance(_content,  Unset):
            content = UNSET
        else:
            content = GetOpenApiResponsePathsActsusernameactorrunsPostRequestBodyContent.from_dict(_content)




        get_open_api_response_paths_actsusernameactorruns_post_request_body = cls(
            required=required,
            content=content,
        )


        get_open_api_response_paths_actsusernameactorruns_post_request_body.additional_properties = d
        return get_open_api_response_paths_actsusernameactorruns_post_request_body

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
