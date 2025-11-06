from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.source_code_file_format import SourceCodeFileFormat






T = TypeVar("T", bound="SourceCodeFile")



@_attrs_define
class SourceCodeFile:
    """ 
        Attributes:
            format_ (SourceCodeFileFormat):  Example: TEXT.
            content (str):  Example: console.log('This is the main.js file');.
            name (str):  Example: src/main.js.
     """

    format_: SourceCodeFileFormat
    content: str
    name: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        format_ = self.format_.value

        content = self.content

        name = self.name


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "format": format_,
            "content": content,
            "name": name,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        format_ = SourceCodeFileFormat(d.pop("format"))




        content = d.pop("content")

        name = d.pop("name")

        source_code_file = cls(
            format_=format_,
            content=content,
            name=name,
        )


        source_code_file.additional_properties = d
        return source_code_file

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
