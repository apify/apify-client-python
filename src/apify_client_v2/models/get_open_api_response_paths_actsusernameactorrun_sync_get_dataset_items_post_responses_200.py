from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset






T = TypeVar("T", bound="GetOpenApiResponsePathsActsusernameactorrunSyncGetDatasetItemsPostResponses200")



@_attrs_define
class GetOpenApiResponsePathsActsusernameactorrunSyncGetDatasetItemsPostResponses200:
    """ 
        Attributes:
            description (str | Unset):  Example: OK.
     """

    description: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        description = self.description


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        description = d.pop("description", UNSET)

        get_open_api_response_paths_actsusernameactorrun_sync_get_dataset_items_post_responses_200 = cls(
            description=description,
        )


        get_open_api_response_paths_actsusernameactorrun_sync_get_dataset_items_post_responses_200.additional_properties = d
        return get_open_api_response_paths_actsusernameactorrun_sync_get_dataset_items_post_responses_200

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
