from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
  from ..models.dataset_schema_validation_error_error_data_invalid_items_item import DatasetSchemaValidationErrorErrorDataInvalidItemsItem





T = TypeVar("T", bound="DatasetSchemaValidationErrorErrorData")



@_attrs_define
class DatasetSchemaValidationErrorErrorData:
    """ 
        Attributes:
            invalid_items (list[DatasetSchemaValidationErrorErrorDataInvalidItemsItem]): A list of invalid items in the
                received array of items.
     """

    invalid_items: list[DatasetSchemaValidationErrorErrorDataInvalidItemsItem]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.dataset_schema_validation_error_error_data_invalid_items_item import DatasetSchemaValidationErrorErrorDataInvalidItemsItem
        invalid_items = []
        for invalid_items_item_data in self.invalid_items:
            invalid_items_item = invalid_items_item_data.to_dict()
            invalid_items.append(invalid_items_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "invalidItems": invalid_items,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.dataset_schema_validation_error_error_data_invalid_items_item import DatasetSchemaValidationErrorErrorDataInvalidItemsItem
        d = dict(src_dict)
        invalid_items = []
        _invalid_items = d.pop("invalidItems")
        for invalid_items_item_data in (_invalid_items):
            invalid_items_item = DatasetSchemaValidationErrorErrorDataInvalidItemsItem.from_dict(invalid_items_item_data)



            invalid_items.append(invalid_items_item)


        dataset_schema_validation_error_error_data = cls(
            invalid_items=invalid_items,
        )


        dataset_schema_validation_error_error_data.additional_properties = d
        return dataset_schema_validation_error_error_data

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
