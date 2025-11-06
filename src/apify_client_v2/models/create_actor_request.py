from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.pay_per_event_actor_pricing_info import PayPerEventActorPricingInfo
  from ..models.default_run_options import DefaultRunOptions
  from ..models.free_actor_pricing_info import FreeActorPricingInfo
  from ..models.version import Version
  from ..models.price_per_dataset_item_actor_pricing_info import PricePerDatasetItemActorPricingInfo
  from ..models.flat_price_per_month_actor_pricing_info import FlatPricePerMonthActorPricingInfo





T = TypeVar("T", bound="CreateActorRequest")



@_attrs_define
class CreateActorRequest:
    """ 
        Attributes:
            name (None | str | Unset):  Example: MyActor.
            description (None | str | Unset):  Example: My favourite actor!.
            title (None | str | Unset):  Example: My actor.
            is_public (bool | None | Unset):
            seo_title (None | str | Unset):  Example: My actor.
            seo_description (None | str | Unset):  Example: My actor is the best.
            restart_on_error (bool | Unset):
            versions (list[Version] | None | Unset):
            pricing_infos (list[FlatPricePerMonthActorPricingInfo | FreeActorPricingInfo | PayPerEventActorPricingInfo |
                PricePerDatasetItemActorPricingInfo] | Unset):
            categories (list[str] | None | Unset):
            default_run_options (DefaultRunOptions | Unset):
     """

    name: None | str | Unset = UNSET
    description: None | str | Unset = UNSET
    title: None | str | Unset = UNSET
    is_public: bool | None | Unset = UNSET
    seo_title: None | str | Unset = UNSET
    seo_description: None | str | Unset = UNSET
    restart_on_error: bool | Unset = UNSET
    versions: list[Version] | None | Unset = UNSET
    pricing_infos: list[FlatPricePerMonthActorPricingInfo | FreeActorPricingInfo | PayPerEventActorPricingInfo | PricePerDatasetItemActorPricingInfo] | Unset = UNSET
    categories: list[str] | None | Unset = UNSET
    default_run_options: DefaultRunOptions | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.pay_per_event_actor_pricing_info import PayPerEventActorPricingInfo
        from ..models.default_run_options import DefaultRunOptions
        from ..models.free_actor_pricing_info import FreeActorPricingInfo
        from ..models.version import Version
        from ..models.price_per_dataset_item_actor_pricing_info import PricePerDatasetItemActorPricingInfo
        from ..models.flat_price_per_month_actor_pricing_info import FlatPricePerMonthActorPricingInfo
        name: None | str | Unset
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        title: None | str | Unset
        if isinstance(self.title, Unset):
            title = UNSET
        else:
            title = self.title

        is_public: bool | None | Unset
        if isinstance(self.is_public, Unset):
            is_public = UNSET
        else:
            is_public = self.is_public

        seo_title: None | str | Unset
        if isinstance(self.seo_title, Unset):
            seo_title = UNSET
        else:
            seo_title = self.seo_title

        seo_description: None | str | Unset
        if isinstance(self.seo_description, Unset):
            seo_description = UNSET
        else:
            seo_description = self.seo_description

        restart_on_error = self.restart_on_error

        versions: list[dict[str, Any]] | None | Unset
        if isinstance(self.versions, Unset):
            versions = UNSET
        elif isinstance(self.versions, list):
            versions = []
            for versions_type_0_item_data in self.versions:
                versions_type_0_item = versions_type_0_item_data.to_dict()
                versions.append(versions_type_0_item)


        else:
            versions = self.versions

        pricing_infos: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.pricing_infos, Unset):
            pricing_infos = []
            for pricing_infos_item_data in self.pricing_infos:
                pricing_infos_item: dict[str, Any]
                if isinstance(pricing_infos_item_data, PayPerEventActorPricingInfo):
                    pricing_infos_item = pricing_infos_item_data.to_dict()
                elif isinstance(pricing_infos_item_data, PricePerDatasetItemActorPricingInfo):
                    pricing_infos_item = pricing_infos_item_data.to_dict()
                elif isinstance(pricing_infos_item_data, FlatPricePerMonthActorPricingInfo):
                    pricing_infos_item = pricing_infos_item_data.to_dict()
                else:
                    pricing_infos_item = pricing_infos_item_data.to_dict()

                pricing_infos.append(pricing_infos_item)



        categories: list[str] | None | Unset
        if isinstance(self.categories, Unset):
            categories = UNSET
        elif isinstance(self.categories, list):
            categories = self.categories


        else:
            categories = self.categories

        default_run_options: dict[str, Any] | Unset = UNSET
        if not isinstance(self.default_run_options, Unset):
            default_run_options = self.default_run_options.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if title is not UNSET:
            field_dict["title"] = title
        if is_public is not UNSET:
            field_dict["isPublic"] = is_public
        if seo_title is not UNSET:
            field_dict["seoTitle"] = seo_title
        if seo_description is not UNSET:
            field_dict["seoDescription"] = seo_description
        if restart_on_error is not UNSET:
            field_dict["restartOnError"] = restart_on_error
        if versions is not UNSET:
            field_dict["versions"] = versions
        if pricing_infos is not UNSET:
            field_dict["pricingInfos"] = pricing_infos
        if categories is not UNSET:
            field_dict["categories"] = categories
        if default_run_options is not UNSET:
            field_dict["defaultRunOptions"] = default_run_options

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.pay_per_event_actor_pricing_info import PayPerEventActorPricingInfo
        from ..models.default_run_options import DefaultRunOptions
        from ..models.free_actor_pricing_info import FreeActorPricingInfo
        from ..models.version import Version
        from ..models.price_per_dataset_item_actor_pricing_info import PricePerDatasetItemActorPricingInfo
        from ..models.flat_price_per_month_actor_pricing_info import FlatPricePerMonthActorPricingInfo
        d = dict(src_dict)
        def _parse_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        name = _parse_name(d.pop("name", UNSET))


        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))


        def _parse_title(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        title = _parse_title(d.pop("title", UNSET))


        def _parse_is_public(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        is_public = _parse_is_public(d.pop("isPublic", UNSET))


        def _parse_seo_title(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        seo_title = _parse_seo_title(d.pop("seoTitle", UNSET))


        def _parse_seo_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        seo_description = _parse_seo_description(d.pop("seoDescription", UNSET))


        restart_on_error = d.pop("restartOnError", UNSET)

        def _parse_versions(data: object) -> list[Version] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                versions_type_0 = []
                _versions_type_0 = data
                for versions_type_0_item_data in (_versions_type_0):
                    versions_type_0_item = Version.from_dict(versions_type_0_item_data)



                    versions_type_0.append(versions_type_0_item)

                return versions_type_0
            except: # noqa: E722
                pass
            return cast(list[Version] | None | Unset, data)

        versions = _parse_versions(d.pop("versions", UNSET))


        pricing_infos = []
        _pricing_infos = d.pop("pricingInfos", UNSET)
        for pricing_infos_item_data in (_pricing_infos or []):
            def _parse_pricing_infos_item(data: object) -> FlatPricePerMonthActorPricingInfo | FreeActorPricingInfo | PayPerEventActorPricingInfo | PricePerDatasetItemActorPricingInfo:
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemas_actor_run_pricing_info_type_0 = PayPerEventActorPricingInfo.from_dict(data)



                    return componentsschemas_actor_run_pricing_info_type_0
                except: # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemas_actor_run_pricing_info_type_1 = PricePerDatasetItemActorPricingInfo.from_dict(data)



                    return componentsschemas_actor_run_pricing_info_type_1
                except: # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemas_actor_run_pricing_info_type_2 = FlatPricePerMonthActorPricingInfo.from_dict(data)



                    return componentsschemas_actor_run_pricing_info_type_2
                except: # noqa: E722
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_actor_run_pricing_info_type_3 = FreeActorPricingInfo.from_dict(data)



                return componentsschemas_actor_run_pricing_info_type_3

            pricing_infos_item = _parse_pricing_infos_item(pricing_infos_item_data)

            pricing_infos.append(pricing_infos_item)


        def _parse_categories(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                categories_type_0 = cast(list[str], data)

                return categories_type_0
            except: # noqa: E722
                pass
            return cast(list[str] | None | Unset, data)

        categories = _parse_categories(d.pop("categories", UNSET))


        _default_run_options = d.pop("defaultRunOptions", UNSET)
        default_run_options: DefaultRunOptions | Unset
        if isinstance(_default_run_options,  Unset):
            default_run_options = UNSET
        else:
            default_run_options = DefaultRunOptions.from_dict(_default_run_options)




        create_actor_request = cls(
            name=name,
            description=description,
            title=title,
            is_public=is_public,
            seo_title=seo_title,
            seo_description=seo_description,
            restart_on_error=restart_on_error,
            versions=versions,
            pricing_infos=pricing_infos,
            categories=categories,
            default_run_options=default_run_options,
        )


        create_actor_request.additional_properties = d
        return create_actor_request

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
