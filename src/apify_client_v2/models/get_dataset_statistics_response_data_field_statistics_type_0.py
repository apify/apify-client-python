from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
  from ..models.dataset_field_statistics import DatasetFieldStatistics





T = TypeVar("T", bound="GetDatasetStatisticsResponseDataFieldStatisticsType0")



@_attrs_define
class GetDatasetStatisticsResponseDataFieldStatisticsType0:
    """ When you configure the dataset [fields schema](https://docs.apify.com/platform/actors/development/actor-
    definition/dataset-schema/validation), we measure the statistics such as `min`, `max`, `nullCount` and `emptyCount`
    for each field. This property provides statistics for each field from dataset fields schema. <br/></br>See dataset
    field statistics [documentation](https://docs.apify.com/platform/actors/development/actor-definition/dataset-
    schema/validation#dataset-field-statistics) for more information.

     """

    additional_properties: dict[str, DatasetFieldStatistics] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.dataset_field_statistics import DatasetFieldStatistics
        
        field_dict: dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = prop.to_dict()


        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.dataset_field_statistics import DatasetFieldStatistics
        d = dict(src_dict)
        get_dataset_statistics_response_data_field_statistics_type_0 = cls(
        )


        additional_properties = {}
        for prop_name, prop_dict in d.items():
            additional_property = DatasetFieldStatistics.from_dict(prop_dict)



            additional_properties[prop_name] = additional_property

        get_dataset_statistics_response_data_field_statistics_type_0.additional_properties = additional_properties
        return get_dataset_statistics_response_data_field_statistics_type_0

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> DatasetFieldStatistics:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: DatasetFieldStatistics) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
