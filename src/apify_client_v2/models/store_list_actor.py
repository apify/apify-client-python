from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.current_pricing_info import CurrentPricingInfo
  from ..models.actor_stats import ActorStats





T = TypeVar("T", bound="StoreListActor")



@_attrs_define
class StoreListActor:
    """ 
        Attributes:
            id (str):  Example: zdc3Pyhyz3m8vjDeM.
            title (str):  Example: My Public Actor.
            name (str):  Example: my-public-actor.
            username (str):  Example: jane35.
            user_full_name (str):  Example: Jane H. Doe.
            description (str):  Example: My public actor!.
            stats (ActorStats):
            current_pricing_info (CurrentPricingInfo):
            categories (list[str] | Unset):  Example: ['MARKETING', 'LEAD_GENERATION'].
            notice (str | Unset):
            picture_url (None | str | Unset):  Example: https://....
            user_picture_url (None | str | Unset):  Example: https://....
            url (None | str | Unset):  Example: https://....
     """

    id: str
    title: str
    name: str
    username: str
    user_full_name: str
    description: str
    stats: ActorStats
    current_pricing_info: CurrentPricingInfo
    categories: list[str] | Unset = UNSET
    notice: str | Unset = UNSET
    picture_url: None | str | Unset = UNSET
    user_picture_url: None | str | Unset = UNSET
    url: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.current_pricing_info import CurrentPricingInfo
        from ..models.actor_stats import ActorStats
        id = self.id

        title = self.title

        name = self.name

        username = self.username

        user_full_name = self.user_full_name

        description = self.description

        stats = self.stats.to_dict()

        current_pricing_info = self.current_pricing_info.to_dict()

        categories: list[str] | Unset = UNSET
        if not isinstance(self.categories, Unset):
            categories = self.categories



        notice = self.notice

        picture_url: None | str | Unset
        if isinstance(self.picture_url, Unset):
            picture_url = UNSET
        else:
            picture_url = self.picture_url

        user_picture_url: None | str | Unset
        if isinstance(self.user_picture_url, Unset):
            user_picture_url = UNSET
        else:
            user_picture_url = self.user_picture_url

        url: None | str | Unset
        if isinstance(self.url, Unset):
            url = UNSET
        else:
            url = self.url


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "title": title,
            "name": name,
            "username": username,
            "userFullName": user_full_name,
            "description": description,
            "stats": stats,
            "currentPricingInfo": current_pricing_info,
        })
        if categories is not UNSET:
            field_dict["categories"] = categories
        if notice is not UNSET:
            field_dict["notice"] = notice
        if picture_url is not UNSET:
            field_dict["pictureUrl"] = picture_url
        if user_picture_url is not UNSET:
            field_dict["userPictureUrl"] = user_picture_url
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.current_pricing_info import CurrentPricingInfo
        from ..models.actor_stats import ActorStats
        d = dict(src_dict)
        id = d.pop("id")

        title = d.pop("title")

        name = d.pop("name")

        username = d.pop("username")

        user_full_name = d.pop("userFullName")

        description = d.pop("description")

        stats = ActorStats.from_dict(d.pop("stats"))




        current_pricing_info = CurrentPricingInfo.from_dict(d.pop("currentPricingInfo"))




        categories = cast(list[str], d.pop("categories", UNSET))


        notice = d.pop("notice", UNSET)

        def _parse_picture_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        picture_url = _parse_picture_url(d.pop("pictureUrl", UNSET))


        def _parse_user_picture_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        user_picture_url = _parse_user_picture_url(d.pop("userPictureUrl", UNSET))


        def _parse_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        url = _parse_url(d.pop("url", UNSET))


        store_list_actor = cls(
            id=id,
            title=title,
            name=name,
            username=username,
            user_full_name=user_full_name,
            description=description,
            stats=stats,
            current_pricing_info=current_pricing_info,
            categories=categories,
            notice=notice,
            picture_url=picture_url,
            user_picture_url=user_picture_url,
            url=url,
        )


        store_list_actor.additional_properties = d
        return store_list_actor

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
