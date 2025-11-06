from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
  from ..models.add_request_response_data import AddRequestResponseData





T = TypeVar("T", bound="RequestQueueRequestsPostResponse201")



@_attrs_define
class RequestQueueRequestsPostResponse201:
    """ 
        Attributes:
            data (AddRequestResponseData):
     """

    data: AddRequestResponseData
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.add_request_response_data import AddRequestResponseData
        data = self.data.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "data": data,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.add_request_response_data import AddRequestResponseData
        d = dict(src_dict)
        data = AddRequestResponseData.from_dict(d.pop("data"))




        request_queue_requests_post_response_201 = cls(
            data=data,
        )


        request_queue_requests_post_response_201.additional_properties = d
        return request_queue_requests_post_response_201

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
