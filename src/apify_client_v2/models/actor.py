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
  from ..models.example_run_input import ExampleRunInput
  from ..models.tagged_builds import TaggedBuilds
  from ..models.free_actor_pricing_info import FreeActorPricingInfo
  from ..models.default_run_options import DefaultRunOptions
  from ..models.version import Version
  from ..models.price_per_dataset_item_actor_pricing_info import PricePerDatasetItemActorPricingInfo
  from ..models.actor_stats import ActorStats
  from ..models.flat_price_per_month_actor_pricing_info import FlatPricePerMonthActorPricingInfo





T = TypeVar("T", bound="Actor")



@_attrs_define
class Actor:
    """ 
        Attributes:
            id (str):  Example: zdc3Pyhyz3m8vjDeM.
            user_id (str):  Example: wRsJZtadYvn4mBZmm.
            name (str):  Example: MyActor.
            username (str):  Example: jane35.
            is_public (bool):
            created_at (str):  Example: 2019-07-08T11:27:57.401Z.
            modified_at (str):  Example: 2019-07-08T14:01:05.546Z.
            stats (ActorStats):
            versions (list[Version]):
            default_run_options (DefaultRunOptions):
            deployment_key (str):  Example: ssh-rsa AAAA ....
            description (None | str | Unset):  Example: My favourite actor!.
            restart_on_error (bool | Unset):
            pricing_infos (list[FlatPricePerMonthActorPricingInfo | FreeActorPricingInfo | PayPerEventActorPricingInfo |
                PricePerDatasetItemActorPricingInfo] | Unset):
            example_run_input (Any | ExampleRunInput | Unset):
            is_deprecated (bool | None | Unset):
            title (None | str | Unset):  Example: My Actor.
            tagged_builds (Any | TaggedBuilds | Unset):
     """

    id: str
    user_id: str
    name: str
    username: str
    is_public: bool
    created_at: str
    modified_at: str
    stats: ActorStats
    versions: list[Version]
    default_run_options: DefaultRunOptions
    deployment_key: str
    description: None | str | Unset = UNSET
    restart_on_error: bool | Unset = UNSET
    pricing_infos: list[FlatPricePerMonthActorPricingInfo | FreeActorPricingInfo | PayPerEventActorPricingInfo | PricePerDatasetItemActorPricingInfo] | Unset = UNSET
    example_run_input: Any | ExampleRunInput | Unset = UNSET
    is_deprecated: bool | None | Unset = UNSET
    title: None | str | Unset = UNSET
    tagged_builds: Any | TaggedBuilds | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.pay_per_event_actor_pricing_info import PayPerEventActorPricingInfo
        from ..models.example_run_input import ExampleRunInput
        from ..models.tagged_builds import TaggedBuilds
        from ..models.free_actor_pricing_info import FreeActorPricingInfo
        from ..models.default_run_options import DefaultRunOptions
        from ..models.version import Version
        from ..models.price_per_dataset_item_actor_pricing_info import PricePerDatasetItemActorPricingInfo
        from ..models.actor_stats import ActorStats
        from ..models.flat_price_per_month_actor_pricing_info import FlatPricePerMonthActorPricingInfo
        id = self.id

        user_id = self.user_id

        name = self.name

        username = self.username

        is_public = self.is_public

        created_at = self.created_at

        modified_at = self.modified_at

        stats = self.stats.to_dict()

        versions = []
        for versions_item_data in self.versions:
            versions_item = versions_item_data.to_dict()
            versions.append(versions_item)



        default_run_options = self.default_run_options.to_dict()

        deployment_key = self.deployment_key

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

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



        example_run_input: Any | dict[str, Any] | Unset
        if isinstance(self.example_run_input, Unset):
            example_run_input = UNSET
        elif isinstance(self.example_run_input, ExampleRunInput):
            example_run_input = self.example_run_input.to_dict()
        else:
            example_run_input = self.example_run_input

        is_deprecated: bool | None | Unset
        if isinstance(self.is_deprecated, Unset):
            is_deprecated = UNSET
        else:
            is_deprecated = self.is_deprecated

        title: None | str | Unset
        if isinstance(self.title, Unset):
            title = UNSET
        else:
            title = self.title

        tagged_builds: Any | dict[str, Any] | Unset
        if isinstance(self.tagged_builds, Unset):
            tagged_builds = UNSET
        elif isinstance(self.tagged_builds, TaggedBuilds):
            tagged_builds = self.tagged_builds.to_dict()
        else:
            tagged_builds = self.tagged_builds


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "userId": user_id,
            "name": name,
            "username": username,
            "isPublic": is_public,
            "createdAt": created_at,
            "modifiedAt": modified_at,
            "stats": stats,
            "versions": versions,
            "defaultRunOptions": default_run_options,
            "deploymentKey": deployment_key,
        })
        if description is not UNSET:
            field_dict["description"] = description
        if restart_on_error is not UNSET:
            field_dict["restartOnError"] = restart_on_error
        if pricing_infos is not UNSET:
            field_dict["pricingInfos"] = pricing_infos
        if example_run_input is not UNSET:
            field_dict["exampleRunInput"] = example_run_input
        if is_deprecated is not UNSET:
            field_dict["isDeprecated"] = is_deprecated
        if title is not UNSET:
            field_dict["title"] = title
        if tagged_builds is not UNSET:
            field_dict["taggedBuilds"] = tagged_builds

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.pay_per_event_actor_pricing_info import PayPerEventActorPricingInfo
        from ..models.example_run_input import ExampleRunInput
        from ..models.tagged_builds import TaggedBuilds
        from ..models.free_actor_pricing_info import FreeActorPricingInfo
        from ..models.default_run_options import DefaultRunOptions
        from ..models.version import Version
        from ..models.price_per_dataset_item_actor_pricing_info import PricePerDatasetItemActorPricingInfo
        from ..models.actor_stats import ActorStats
        from ..models.flat_price_per_month_actor_pricing_info import FlatPricePerMonthActorPricingInfo
        d = dict(src_dict)
        id = d.pop("id")

        user_id = d.pop("userId")

        name = d.pop("name")

        username = d.pop("username")

        is_public = d.pop("isPublic")

        created_at = d.pop("createdAt")

        modified_at = d.pop("modifiedAt")

        stats = ActorStats.from_dict(d.pop("stats"))




        versions = []
        _versions = d.pop("versions")
        for versions_item_data in (_versions):
            versions_item = Version.from_dict(versions_item_data)



            versions.append(versions_item)


        default_run_options = DefaultRunOptions.from_dict(d.pop("defaultRunOptions"))




        deployment_key = d.pop("deploymentKey")

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))


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


        def _parse_example_run_input(data: object) -> Any | ExampleRunInput | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                example_run_input_type_1 = ExampleRunInput.from_dict(data)



                return example_run_input_type_1
            except: # noqa: E722
                pass
            return cast(Any | ExampleRunInput | Unset, data)

        example_run_input = _parse_example_run_input(d.pop("exampleRunInput", UNSET))


        def _parse_is_deprecated(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        is_deprecated = _parse_is_deprecated(d.pop("isDeprecated", UNSET))


        def _parse_title(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        title = _parse_title(d.pop("title", UNSET))


        def _parse_tagged_builds(data: object) -> Any | TaggedBuilds | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                tagged_builds_type_1 = TaggedBuilds.from_dict(data)



                return tagged_builds_type_1
            except: # noqa: E722
                pass
            return cast(Any | TaggedBuilds | Unset, data)

        tagged_builds = _parse_tagged_builds(d.pop("taggedBuilds", UNSET))


        actor = cls(
            id=id,
            user_id=user_id,
            name=name,
            username=username,
            is_public=is_public,
            created_at=created_at,
            modified_at=modified_at,
            stats=stats,
            versions=versions,
            default_run_options=default_run_options,
            deployment_key=deployment_key,
            description=description,
            restart_on_error=restart_on_error,
            pricing_infos=pricing_infos,
            example_run_input=example_run_input,
            is_deprecated=is_deprecated,
            title=title,
            tagged_builds=tagged_builds,
        )


        actor.additional_properties = d
        return actor

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
