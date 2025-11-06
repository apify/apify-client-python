from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.act_update_tagged_builds_type_0 import ActUpdateTaggedBuildsType0
  from ..models.pay_per_event_actor_pricing_info import PayPerEventActorPricingInfo
  from ..models.default_run_options import DefaultRunOptions
  from ..models.free_actor_pricing_info import FreeActorPricingInfo
  from ..models.price_per_dataset_item_actor_pricing_info import PricePerDatasetItemActorPricingInfo
  from ..models.flat_price_per_month_actor_pricing_info import FlatPricePerMonthActorPricingInfo
  from ..models.create_or_update_env_var_request import CreateOrUpdateEnvVarRequest





T = TypeVar("T", bound="ActUpdate")



@_attrs_define
class ActUpdate:
    """ 
        Attributes:
            name (str):  Example: MyActor.
            is_public (bool):
            versions (list[CreateOrUpdateEnvVarRequest]):
            description (None | str | Unset):  Example: My favourite actor!.
            seo_title (None | str | Unset):  Example: My actor.
            seo_description (None | str | Unset):  Example: My actor is the best.
            title (None | str | Unset):  Example: My Actor.
            restart_on_error (bool | Unset):
            pricing_infos (list[FlatPricePerMonthActorPricingInfo | FreeActorPricingInfo | PayPerEventActorPricingInfo |
                PricePerDatasetItemActorPricingInfo] | Unset):
            categories (list[str] | None | Unset):
            default_run_options (DefaultRunOptions | Unset):
            tagged_builds (ActUpdateTaggedBuildsType0 | None | Unset): An object to modify tags on the Actor's builds. The
                key is the tag name (e.g., _latest_), and the value is either an object with a `buildId` or `null`.

                This operation is a patch; any existing tags that you omit from this object will be preserved.

                - **To create or reassign a tag**, provide the tag name with a `buildId`. e.g., to assign the _latest_ tag:

                  &nbsp;

                  ```json
                  {
                    "latest": {
                      "buildId": "z2EryhbfhgSyqj6Hn"
                    }
                  }
                  ```

                - **To remove a tag**, provide the tag name with a `null` value. e.g., to remove the _beta_ tag:

                  &nbsp;

                  ```json
                  {
                    "beta": null
                  }
                  ```

                - **To perform multiple operations**, combine them. The following reassigns _latest_ and removes _beta_, while
                preserving any other existing tags.

                  &nbsp;

                  ```json
                  {
                    "latest": {
                      "buildId": "z2EryhbfhgSyqj6Hn"
                    },
                    "beta": null
                  }
                  ```
                 Example: {'latest': {'buildId': 'z2EryhbfhgSyqj6Hn'}, 'beta': None}.
     """

    name: str
    is_public: bool
    versions: list[CreateOrUpdateEnvVarRequest]
    description: None | str | Unset = UNSET
    seo_title: None | str | Unset = UNSET
    seo_description: None | str | Unset = UNSET
    title: None | str | Unset = UNSET
    restart_on_error: bool | Unset = UNSET
    pricing_infos: list[FlatPricePerMonthActorPricingInfo | FreeActorPricingInfo | PayPerEventActorPricingInfo | PricePerDatasetItemActorPricingInfo] | Unset = UNSET
    categories: list[str] | None | Unset = UNSET
    default_run_options: DefaultRunOptions | Unset = UNSET
    tagged_builds: ActUpdateTaggedBuildsType0 | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.act_update_tagged_builds_type_0 import ActUpdateTaggedBuildsType0
        from ..models.pay_per_event_actor_pricing_info import PayPerEventActorPricingInfo
        from ..models.default_run_options import DefaultRunOptions
        from ..models.free_actor_pricing_info import FreeActorPricingInfo
        from ..models.price_per_dataset_item_actor_pricing_info import PricePerDatasetItemActorPricingInfo
        from ..models.flat_price_per_month_actor_pricing_info import FlatPricePerMonthActorPricingInfo
        from ..models.create_or_update_env_var_request import CreateOrUpdateEnvVarRequest
        name = self.name

        is_public = self.is_public

        versions = []
        for versions_item_data in self.versions:
            versions_item = versions_item_data.to_dict()
            versions.append(versions_item)



        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

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

        title: None | str | Unset
        if isinstance(self.title, Unset):
            title = UNSET
        else:
            title = self.title

        restart_on_error = self.restart_on_error

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

        tagged_builds: dict[str, Any] | None | Unset
        if isinstance(self.tagged_builds, Unset):
            tagged_builds = UNSET
        elif isinstance(self.tagged_builds, ActUpdateTaggedBuildsType0):
            tagged_builds = self.tagged_builds.to_dict()
        else:
            tagged_builds = self.tagged_builds


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "name": name,
            "isPublic": is_public,
            "versions": versions,
        })
        if description is not UNSET:
            field_dict["description"] = description
        if seo_title is not UNSET:
            field_dict["seoTitle"] = seo_title
        if seo_description is not UNSET:
            field_dict["seoDescription"] = seo_description
        if title is not UNSET:
            field_dict["title"] = title
        if restart_on_error is not UNSET:
            field_dict["restartOnError"] = restart_on_error
        if pricing_infos is not UNSET:
            field_dict["pricingInfos"] = pricing_infos
        if categories is not UNSET:
            field_dict["categories"] = categories
        if default_run_options is not UNSET:
            field_dict["defaultRunOptions"] = default_run_options
        if tagged_builds is not UNSET:
            field_dict["taggedBuilds"] = tagged_builds

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.act_update_tagged_builds_type_0 import ActUpdateTaggedBuildsType0
        from ..models.pay_per_event_actor_pricing_info import PayPerEventActorPricingInfo
        from ..models.default_run_options import DefaultRunOptions
        from ..models.free_actor_pricing_info import FreeActorPricingInfo
        from ..models.price_per_dataset_item_actor_pricing_info import PricePerDatasetItemActorPricingInfo
        from ..models.flat_price_per_month_actor_pricing_info import FlatPricePerMonthActorPricingInfo
        from ..models.create_or_update_env_var_request import CreateOrUpdateEnvVarRequest
        d = dict(src_dict)
        name = d.pop("name")

        is_public = d.pop("isPublic")

        versions = []
        _versions = d.pop("versions")
        for versions_item_data in (_versions):
            versions_item = CreateOrUpdateEnvVarRequest.from_dict(versions_item_data)



            versions.append(versions_item)


        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))


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


        def _parse_title(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        title = _parse_title(d.pop("title", UNSET))


        restart_on_error = d.pop("restartOnError", UNSET)

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




        def _parse_tagged_builds(data: object) -> ActUpdateTaggedBuildsType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                tagged_builds_type_0 = ActUpdateTaggedBuildsType0.from_dict(data)



                return tagged_builds_type_0
            except: # noqa: E722
                pass
            return cast(ActUpdateTaggedBuildsType0 | None | Unset, data)

        tagged_builds = _parse_tagged_builds(d.pop("taggedBuilds", UNSET))


        act_update = cls(
            name=name,
            is_public=is_public,
            versions=versions,
            description=description,
            seo_title=seo_title,
            seo_description=seo_description,
            title=title,
            restart_on_error=restart_on_error,
            pricing_infos=pricing_infos,
            categories=categories,
            default_run_options=default_run_options,
            tagged_builds=tagged_builds,
        )


        act_update.additional_properties = d
        return act_update

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
