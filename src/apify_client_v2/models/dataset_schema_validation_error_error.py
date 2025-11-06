from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
  from ..models.dataset_schema_validation_error_error_data import DatasetSchemaValidationErrorErrorData





T = TypeVar("T", bound="DatasetSchemaValidationErrorError")



@_attrs_define
class DatasetSchemaValidationErrorError:
    """ 
        Attributes:
            type_ (str): The type of the error. Example: schema-validation-error.
            message (str): A human-readable message describing the error. Example: Schema validation failed.
            data (DatasetSchemaValidationErrorErrorData):
     """

    type_: str
    message: str
    data: DatasetSchemaValidationErrorErrorData
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.dataset_schema_validation_error_error_data import DatasetSchemaValidationErrorErrorData
        type_ = self.type_

        message = self.message

        data = self.data.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "type": type_,
            "message": message,
            "data": data,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.dataset_schema_validation_error_error_data import DatasetSchemaValidationErrorErrorData
        d = dict(src_dict)
        type_ = d.pop("type")

        message = d.pop("message")

        data = DatasetSchemaValidationErrorErrorData.from_dict(d.pop("data"))




        dataset_schema_validation_error_error = cls(
            type_=type_,
            message=message,
            data=data,
        )


        dataset_schema_validation_error_error.additional_properties = d
        return dataset_schema_validation_error_error

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
