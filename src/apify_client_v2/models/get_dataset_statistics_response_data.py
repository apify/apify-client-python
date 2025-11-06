from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.get_dataset_statistics_response_data_field_statistics_type_0 import GetDatasetStatisticsResponseDataFieldStatisticsType0





T = TypeVar("T", bound="GetDatasetStatisticsResponseData")



@_attrs_define
class GetDatasetStatisticsResponseData:
    """ 
        Attributes:
            field_statistics (GetDatasetStatisticsResponseDataFieldStatisticsType0 | None | Unset): When you configure the
                dataset [fields schema](https://docs.apify.com/platform/actors/development/actor-definition/dataset-
                schema/validation), we measure the statistics such as `min`, `max`, `nullCount` and `emptyCount` for each field.
                This property provides statistics for each field from dataset fields schema. <br/></br>See dataset field
                statistics [documentation](https://docs.apify.com/platform/actors/development/actor-definition/dataset-
                schema/validation#dataset-field-statistics) for more information.
     """

    field_statistics: GetDatasetStatisticsResponseDataFieldStatisticsType0 | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.get_dataset_statistics_response_data_field_statistics_type_0 import GetDatasetStatisticsResponseDataFieldStatisticsType0
        field_statistics: dict[str, Any] | None | Unset
        if isinstance(self.field_statistics, Unset):
            field_statistics = UNSET
        elif isinstance(self.field_statistics, GetDatasetStatisticsResponseDataFieldStatisticsType0):
            field_statistics = self.field_statistics.to_dict()
        else:
            field_statistics = self.field_statistics


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if field_statistics is not UNSET:
            field_dict["fieldStatistics"] = field_statistics

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_dataset_statistics_response_data_field_statistics_type_0 import GetDatasetStatisticsResponseDataFieldStatisticsType0
        d = dict(src_dict)
        def _parse_field_statistics(data: object) -> GetDatasetStatisticsResponseDataFieldStatisticsType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                field_statistics_type_0 = GetDatasetStatisticsResponseDataFieldStatisticsType0.from_dict(data)



                return field_statistics_type_0
            except: # noqa: E722
                pass
            return cast(GetDatasetStatisticsResponseDataFieldStatisticsType0 | None | Unset, data)

        field_statistics = _parse_field_statistics(d.pop("fieldStatistics", UNSET))


        get_dataset_statistics_response_data = cls(
            field_statistics=field_statistics,
        )


        get_dataset_statistics_response_data.additional_properties = d
        return get_dataset_statistics_response_data

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
