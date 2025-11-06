from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.dataset_schema_validation_error_error import DatasetSchemaValidationErrorError





T = TypeVar("T", bound="DatasetSchemaValidationError")



@_attrs_define
class DatasetSchemaValidationError:
    """ 
        Attributes:
            error (DatasetSchemaValidationErrorError | Unset):
     """

    error: DatasetSchemaValidationErrorError | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.dataset_schema_validation_error_error import DatasetSchemaValidationErrorError
        error: dict[str, Any] | Unset = UNSET
        if not isinstance(self.error, Unset):
            error = self.error.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if error is not UNSET:
            field_dict["error"] = error

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.dataset_schema_validation_error_error import DatasetSchemaValidationErrorError
        d = dict(src_dict)
        _error = d.pop("error", UNSET)
        error: DatasetSchemaValidationErrorError | Unset
        if isinstance(_error,  Unset):
            error = UNSET
        else:
            error = DatasetSchemaValidationErrorError.from_dict(_error)




        dataset_schema_validation_error = cls(
            error=error,
        )


        dataset_schema_validation_error.additional_properties = d
        return dataset_schema_validation_error

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
