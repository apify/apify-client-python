from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.actor_definition_storages_dataset import ActorDefinitionStoragesDataset





T = TypeVar("T", bound="ActorDefinitionStorages")



@_attrs_define
class ActorDefinitionStorages:
    """ 
        Attributes:
            dataset (ActorDefinitionStoragesDataset | Unset): Defines the schema of items in your dataset, the full
                specification can be found in [Apify docs](https://docs.apify.com/platform/actors/development/actor-
                definition/dataset-schema)
     """

    dataset: ActorDefinitionStoragesDataset | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.actor_definition_storages_dataset import ActorDefinitionStoragesDataset
        dataset: dict[str, Any] | Unset = UNSET
        if not isinstance(self.dataset, Unset):
            dataset = self.dataset.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if dataset is not UNSET:
            field_dict["dataset"] = dataset

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.actor_definition_storages_dataset import ActorDefinitionStoragesDataset
        d = dict(src_dict)
        _dataset = d.pop("dataset", UNSET)
        dataset: ActorDefinitionStoragesDataset | Unset
        if isinstance(_dataset,  Unset):
            dataset = UNSET
        else:
            dataset = ActorDefinitionStoragesDataset.from_dict(_dataset)




        actor_definition_storages = cls(
            dataset=dataset,
        )


        actor_definition_storages.additional_properties = d
        return actor_definition_storages

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
