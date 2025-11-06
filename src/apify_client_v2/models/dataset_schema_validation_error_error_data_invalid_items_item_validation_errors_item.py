from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.dataset_schema_validation_error_error_data_invalid_items_item_validation_errors_item_params import DatasetSchemaValidationErrorErrorDataInvalidItemsItemValidationErrorsItemParams





T = TypeVar("T", bound="DatasetSchemaValidationErrorErrorDataInvalidItemsItemValidationErrorsItem")



@_attrs_define
class DatasetSchemaValidationErrorErrorDataInvalidItemsItemValidationErrorsItem:
    """ 
        Attributes:
            instance_path (str | Unset): The path to the instance being validated.
            schema_path (str | Unset): The path to the schema that failed the validation.
            keyword (str | Unset): The validation keyword that caused the error.
            message (str | Unset): A message describing the validation error.
            params (DatasetSchemaValidationErrorErrorDataInvalidItemsItemValidationErrorsItemParams | Unset): Additional
                parameters specific to the validation error.
     """

    instance_path: str | Unset = UNSET
    schema_path: str | Unset = UNSET
    keyword: str | Unset = UNSET
    message: str | Unset = UNSET
    params: DatasetSchemaValidationErrorErrorDataInvalidItemsItemValidationErrorsItemParams | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.dataset_schema_validation_error_error_data_invalid_items_item_validation_errors_item_params import DatasetSchemaValidationErrorErrorDataInvalidItemsItemValidationErrorsItemParams
        instance_path = self.instance_path

        schema_path = self.schema_path

        keyword = self.keyword

        message = self.message

        params: dict[str, Any] | Unset = UNSET
        if not isinstance(self.params, Unset):
            params = self.params.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if instance_path is not UNSET:
            field_dict["instancePath"] = instance_path
        if schema_path is not UNSET:
            field_dict["schemaPath"] = schema_path
        if keyword is not UNSET:
            field_dict["keyword"] = keyword
        if message is not UNSET:
            field_dict["message"] = message
        if params is not UNSET:
            field_dict["params"] = params

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.dataset_schema_validation_error_error_data_invalid_items_item_validation_errors_item_params import DatasetSchemaValidationErrorErrorDataInvalidItemsItemValidationErrorsItemParams
        d = dict(src_dict)
        instance_path = d.pop("instancePath", UNSET)

        schema_path = d.pop("schemaPath", UNSET)

        keyword = d.pop("keyword", UNSET)

        message = d.pop("message", UNSET)

        _params = d.pop("params", UNSET)
        params: DatasetSchemaValidationErrorErrorDataInvalidItemsItemValidationErrorsItemParams | Unset
        if isinstance(_params,  Unset):
            params = UNSET
        else:
            params = DatasetSchemaValidationErrorErrorDataInvalidItemsItemValidationErrorsItemParams.from_dict(_params)




        dataset_schema_validation_error_error_data_invalid_items_item_validation_errors_item = cls(
            instance_path=instance_path,
            schema_path=schema_path,
            keyword=keyword,
            message=message,
            params=params,
        )


        dataset_schema_validation_error_error_data_invalid_items_item_validation_errors_item.additional_properties = d
        return dataset_schema_validation_error_error_data_invalid_items_item_validation_errors_item

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
