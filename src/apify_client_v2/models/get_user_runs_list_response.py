from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
  from ..models.get_user_runs_list_response_data import GetUserRunsListResponseData





T = TypeVar("T", bound="GetUserRunsListResponse")



@_attrs_define
class GetUserRunsListResponse:
    """ 
        Attributes:
            data (GetUserRunsListResponseData):
     """

    data: GetUserRunsListResponseData
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.get_user_runs_list_response_data import GetUserRunsListResponseData
        data = self.data.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "data": data,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_user_runs_list_response_data import GetUserRunsListResponseData
        d = dict(src_dict)
        data = GetUserRunsListResponseData.from_dict(d.pop("data"))




        get_user_runs_list_response = cls(
            data=data,
        )


        get_user_runs_list_response.additional_properties = d
        return get_user_runs_list_response

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
