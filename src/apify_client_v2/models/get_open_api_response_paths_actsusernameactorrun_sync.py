from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.get_open_api_response_paths_actsusernameactorrun_sync_post import GetOpenApiResponsePathsActsusernameactorrunSyncPost





T = TypeVar("T", bound="GetOpenApiResponsePathsActsusernameactorrunSync")



@_attrs_define
class GetOpenApiResponsePathsActsusernameactorrunSync:
    """ 
        Attributes:
            post (GetOpenApiResponsePathsActsusernameactorrunSyncPost | Unset):
     """

    post: GetOpenApiResponsePathsActsusernameactorrunSyncPost | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.get_open_api_response_paths_actsusernameactorrun_sync_post import GetOpenApiResponsePathsActsusernameactorrunSyncPost
        post: dict[str, Any] | Unset = UNSET
        if not isinstance(self.post, Unset):
            post = self.post.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if post is not UNSET:
            field_dict["post"] = post

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_open_api_response_paths_actsusernameactorrun_sync_post import GetOpenApiResponsePathsActsusernameactorrunSyncPost
        d = dict(src_dict)
        _post = d.pop("post", UNSET)
        post: GetOpenApiResponsePathsActsusernameactorrunSyncPost | Unset
        if isinstance(_post,  Unset):
            post = UNSET
        else:
            post = GetOpenApiResponsePathsActsusernameactorrunSyncPost.from_dict(_post)




        get_open_api_response_paths_actsusernameactorrun_sync = cls(
            post=post,
        )


        get_open_api_response_paths_actsusernameactorrun_sync.additional_properties = d
        return get_open_api_response_paths_actsusernameactorrun_sync

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
