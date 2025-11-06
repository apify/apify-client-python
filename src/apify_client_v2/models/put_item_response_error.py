from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
  from ..models.put_item_response_error_error import PutItemResponseErrorError





T = TypeVar("T", bound="PutItemResponseError")



@_attrs_define
class PutItemResponseError:
    """ 
        Attributes:
            error (PutItemResponseErrorError):
     """

    error: PutItemResponseErrorError
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.put_item_response_error_error import PutItemResponseErrorError
        error = self.error.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "error": error,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.put_item_response_error_error import PutItemResponseErrorError
        d = dict(src_dict)
        error = PutItemResponseErrorError.from_dict(d.pop("error"))




        put_item_response_error = cls(
            error=error,
        )


        put_item_response_error.additional_properties = d
        return put_item_response_error

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
