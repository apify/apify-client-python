from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset







T = TypeVar("T", bound="RequestQueueRequestsUnlockPostResponse200Data")



@_attrs_define
class RequestQueueRequestsUnlockPostResponse200Data:
    """ 
        Attributes:
            unlocked_count (int): Number of requests that were successfully unlocked
     """

    unlocked_count: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        unlocked_count = self.unlocked_count


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "unlockedCount": unlocked_count,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        unlocked_count = d.pop("unlockedCount")

        request_queue_requests_unlock_post_response_200_data = cls(
            unlocked_count=unlocked_count,
        )


        request_queue_requests_unlock_post_response_200_data.additional_properties = d
        return request_queue_requests_unlock_post_response_200_data

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
