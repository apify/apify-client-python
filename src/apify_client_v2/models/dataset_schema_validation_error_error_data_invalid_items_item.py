from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.dataset_schema_validation_error_error_data_invalid_items_item_validation_errors_item import DatasetSchemaValidationErrorErrorDataInvalidItemsItemValidationErrorsItem





T = TypeVar("T", bound="DatasetSchemaValidationErrorErrorDataInvalidItemsItem")



@_attrs_define
class DatasetSchemaValidationErrorErrorDataInvalidItemsItem:
    """ 
        Attributes:
            item_position (float | Unset): The position of the invalid item in the array. Example: 2.
            validation_errors (list[DatasetSchemaValidationErrorErrorDataInvalidItemsItemValidationErrorsItem] | Unset): A
                complete list of AJV validation error objects for the invalid item.
     """

    item_position: float | Unset = UNSET
    validation_errors: list[DatasetSchemaValidationErrorErrorDataInvalidItemsItemValidationErrorsItem] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.dataset_schema_validation_error_error_data_invalid_items_item_validation_errors_item import DatasetSchemaValidationErrorErrorDataInvalidItemsItemValidationErrorsItem
        item_position = self.item_position

        validation_errors: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.validation_errors, Unset):
            validation_errors = []
            for validation_errors_item_data in self.validation_errors:
                validation_errors_item = validation_errors_item_data.to_dict()
                validation_errors.append(validation_errors_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if item_position is not UNSET:
            field_dict["itemPosition"] = item_position
        if validation_errors is not UNSET:
            field_dict["validationErrors"] = validation_errors

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.dataset_schema_validation_error_error_data_invalid_items_item_validation_errors_item import DatasetSchemaValidationErrorErrorDataInvalidItemsItemValidationErrorsItem
        d = dict(src_dict)
        item_position = d.pop("itemPosition", UNSET)

        validation_errors = []
        _validation_errors = d.pop("validationErrors", UNSET)
        for validation_errors_item_data in (_validation_errors or []):
            validation_errors_item = DatasetSchemaValidationErrorErrorDataInvalidItemsItemValidationErrorsItem.from_dict(validation_errors_item_data)



            validation_errors.append(validation_errors_item)


        dataset_schema_validation_error_error_data_invalid_items_item = cls(
            item_position=item_position,
            validation_errors=validation_errors,
        )


        dataset_schema_validation_error_error_data_invalid_items_item.additional_properties = d
        return dataset_schema_validation_error_error_data_invalid_items_item

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
