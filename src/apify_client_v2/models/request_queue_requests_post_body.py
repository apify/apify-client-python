from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset







T = TypeVar("T", bound="RequestQueueRequestsPostBody")



@_attrs_define
class RequestQueueRequestsPostBody:
    """ 
        Attributes:
            unique_key (str):  Example: http://example.com.
            url (str):  Example: http://example.com.
            method (str):  Example: GET.
     """

    unique_key: str
    url: str
    method: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        unique_key = self.unique_key

        url = self.url

        method = self.method


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "uniqueKey": unique_key,
            "url": url,
            "method": method,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        unique_key = d.pop("uniqueKey")

        url = d.pop("url")

        method = d.pop("method")

        request_queue_requests_post_body = cls(
            unique_key=unique_key,
            url=url,
            method=method,
        )


        request_queue_requests_post_body.additional_properties = d
        return request_queue_requests_post_body

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
