from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
  from ..models.effective_platform_feature import EffectivePlatformFeature





T = TypeVar("T", bound="EffectivePlatformFeatures")



@_attrs_define
class EffectivePlatformFeatures:
    """ 
        Attributes:
            actors (EffectivePlatformFeature):
            storage (EffectivePlatformFeature):
            scheduler (EffectivePlatformFeature):
            proxy (EffectivePlatformFeature):
            proxy_external_access (EffectivePlatformFeature):
            proxy_residential (EffectivePlatformFeature):
            proxy_serps (EffectivePlatformFeature):
            webhooks (EffectivePlatformFeature):
            actors_public_all (EffectivePlatformFeature):
            actors_public_developer (EffectivePlatformFeature):
     """

    actors: EffectivePlatformFeature
    storage: EffectivePlatformFeature
    scheduler: EffectivePlatformFeature
    proxy: EffectivePlatformFeature
    proxy_external_access: EffectivePlatformFeature
    proxy_residential: EffectivePlatformFeature
    proxy_serps: EffectivePlatformFeature
    webhooks: EffectivePlatformFeature
    actors_public_all: EffectivePlatformFeature
    actors_public_developer: EffectivePlatformFeature
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.effective_platform_feature import EffectivePlatformFeature
        actors = self.actors.to_dict()

        storage = self.storage.to_dict()

        scheduler = self.scheduler.to_dict()

        proxy = self.proxy.to_dict()

        proxy_external_access = self.proxy_external_access.to_dict()

        proxy_residential = self.proxy_residential.to_dict()

        proxy_serps = self.proxy_serps.to_dict()

        webhooks = self.webhooks.to_dict()

        actors_public_all = self.actors_public_all.to_dict()

        actors_public_developer = self.actors_public_developer.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "ACTORS": actors,
            "STORAGE": storage,
            "SCHEDULER": scheduler,
            "PROXY": proxy,
            "PROXY_EXTERNAL_ACCESS": proxy_external_access,
            "PROXY_RESIDENTIAL": proxy_residential,
            "PROXY_SERPS": proxy_serps,
            "WEBHOOKS": webhooks,
            "ACTORS_PUBLIC_ALL": actors_public_all,
            "ACTORS_PUBLIC_DEVELOPER": actors_public_developer,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.effective_platform_feature import EffectivePlatformFeature
        d = dict(src_dict)
        actors = EffectivePlatformFeature.from_dict(d.pop("ACTORS"))




        storage = EffectivePlatformFeature.from_dict(d.pop("STORAGE"))




        scheduler = EffectivePlatformFeature.from_dict(d.pop("SCHEDULER"))




        proxy = EffectivePlatformFeature.from_dict(d.pop("PROXY"))




        proxy_external_access = EffectivePlatformFeature.from_dict(d.pop("PROXY_EXTERNAL_ACCESS"))




        proxy_residential = EffectivePlatformFeature.from_dict(d.pop("PROXY_RESIDENTIAL"))




        proxy_serps = EffectivePlatformFeature.from_dict(d.pop("PROXY_SERPS"))




        webhooks = EffectivePlatformFeature.from_dict(d.pop("WEBHOOKS"))




        actors_public_all = EffectivePlatformFeature.from_dict(d.pop("ACTORS_PUBLIC_ALL"))




        actors_public_developer = EffectivePlatformFeature.from_dict(d.pop("ACTORS_PUBLIC_DEVELOPER"))




        effective_platform_features = cls(
            actors=actors,
            storage=storage,
            scheduler=scheduler,
            proxy=proxy,
            proxy_external_access=proxy_external_access,
            proxy_residential=proxy_residential,
            proxy_serps=proxy_serps,
            webhooks=webhooks,
            actors_public_all=actors_public_all,
            actors_public_developer=actors_public_developer,
        )


        effective_platform_features.additional_properties = d
        return effective_platform_features

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
