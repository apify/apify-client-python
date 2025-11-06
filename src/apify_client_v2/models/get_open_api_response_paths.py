from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.get_open_api_response_paths_actsusernameactorrun_sync_get_dataset_items import GetOpenApiResponsePathsActsusernameactorrunSyncGetDatasetItems
  from ..models.get_open_api_response_paths_actsusernameactorruns import GetOpenApiResponsePathsActsusernameactorruns
  from ..models.get_open_api_response_paths_actsusernameactorrun_sync import GetOpenApiResponsePathsActsusernameactorrunSync





T = TypeVar("T", bound="GetOpenApiResponsePaths")



@_attrs_define
class GetOpenApiResponsePaths:
    """ 
        Attributes:
            actsusernameactorrun_sync_get_dataset_items (GetOpenApiResponsePathsActsusernameactorrunSyncGetDatasetItems |
                Unset):
            actsusernameactorruns (GetOpenApiResponsePathsActsusernameactorruns | Unset):
            actsusernameactorrun_sync (GetOpenApiResponsePathsActsusernameactorrunSync | Unset):
     """

    actsusernameactorrun_sync_get_dataset_items: GetOpenApiResponsePathsActsusernameactorrunSyncGetDatasetItems | Unset = UNSET
    actsusernameactorruns: GetOpenApiResponsePathsActsusernameactorruns | Unset = UNSET
    actsusernameactorrun_sync: GetOpenApiResponsePathsActsusernameactorrunSync | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.get_open_api_response_paths_actsusernameactorrun_sync_get_dataset_items import GetOpenApiResponsePathsActsusernameactorrunSyncGetDatasetItems
        from ..models.get_open_api_response_paths_actsusernameactorruns import GetOpenApiResponsePathsActsusernameactorruns
        from ..models.get_open_api_response_paths_actsusernameactorrun_sync import GetOpenApiResponsePathsActsusernameactorrunSync
        actsusernameactorrun_sync_get_dataset_items: dict[str, Any] | Unset = UNSET
        if not isinstance(self.actsusernameactorrun_sync_get_dataset_items, Unset):
            actsusernameactorrun_sync_get_dataset_items = self.actsusernameactorrun_sync_get_dataset_items.to_dict()

        actsusernameactorruns: dict[str, Any] | Unset = UNSET
        if not isinstance(self.actsusernameactorruns, Unset):
            actsusernameactorruns = self.actsusernameactorruns.to_dict()

        actsusernameactorrun_sync: dict[str, Any] | Unset = UNSET
        if not isinstance(self.actsusernameactorrun_sync, Unset):
            actsusernameactorrun_sync = self.actsusernameactorrun_sync.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if actsusernameactorrun_sync_get_dataset_items is not UNSET:
            field_dict["/acts/<username>~<actor>/run-sync-get-dataset-items"] = actsusernameactorrun_sync_get_dataset_items
        if actsusernameactorruns is not UNSET:
            field_dict["/acts/<username>~<actor>/runs"] = actsusernameactorruns
        if actsusernameactorrun_sync is not UNSET:
            field_dict["/acts/<username>~<actor>/run-sync"] = actsusernameactorrun_sync

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_open_api_response_paths_actsusernameactorrun_sync_get_dataset_items import GetOpenApiResponsePathsActsusernameactorrunSyncGetDatasetItems
        from ..models.get_open_api_response_paths_actsusernameactorruns import GetOpenApiResponsePathsActsusernameactorruns
        from ..models.get_open_api_response_paths_actsusernameactorrun_sync import GetOpenApiResponsePathsActsusernameactorrunSync
        d = dict(src_dict)
        _actsusernameactorrun_sync_get_dataset_items = d.pop("/acts/<username>~<actor>/run-sync-get-dataset-items", UNSET)
        actsusernameactorrun_sync_get_dataset_items: GetOpenApiResponsePathsActsusernameactorrunSyncGetDatasetItems | Unset
        if isinstance(_actsusernameactorrun_sync_get_dataset_items,  Unset):
            actsusernameactorrun_sync_get_dataset_items = UNSET
        else:
            actsusernameactorrun_sync_get_dataset_items = GetOpenApiResponsePathsActsusernameactorrunSyncGetDatasetItems.from_dict(_actsusernameactorrun_sync_get_dataset_items)




        _actsusernameactorruns = d.pop("/acts/<username>~<actor>/runs", UNSET)
        actsusernameactorruns: GetOpenApiResponsePathsActsusernameactorruns | Unset
        if isinstance(_actsusernameactorruns,  Unset):
            actsusernameactorruns = UNSET
        else:
            actsusernameactorruns = GetOpenApiResponsePathsActsusernameactorruns.from_dict(_actsusernameactorruns)




        _actsusernameactorrun_sync = d.pop("/acts/<username>~<actor>/run-sync", UNSET)
        actsusernameactorrun_sync: GetOpenApiResponsePathsActsusernameactorrunSync | Unset
        if isinstance(_actsusernameactorrun_sync,  Unset):
            actsusernameactorrun_sync = UNSET
        else:
            actsusernameactorrun_sync = GetOpenApiResponsePathsActsusernameactorrunSync.from_dict(_actsusernameactorrun_sync)




        get_open_api_response_paths = cls(
            actsusernameactorrun_sync_get_dataset_items=actsusernameactorrun_sync_get_dataset_items,
            actsusernameactorruns=actsusernameactorruns,
            actsusernameactorrun_sync=actsusernameactorrun_sync,
        )


        get_open_api_response_paths.additional_properties = d
        return get_open_api_response_paths

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
