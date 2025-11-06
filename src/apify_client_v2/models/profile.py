from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset






T = TypeVar("T", bound="Profile")



@_attrs_define
class Profile:
    """ 
        Attributes:
            bio (str | Unset):  Example: I started web scraping in 1985 using Altair BASIC..
            name (str | Unset):  Example: Jane Doe.
            picture_url (str | Unset):  Example: /img/anonymous_user_picture.png.
            github_username (str | Unset):  Example: torvalds..
            website_url (str | Unset):  Example: http://www.example.com.
            twitter_username (str | Unset):  Example: @BillGates.
     """

    bio: str | Unset = UNSET
    name: str | Unset = UNSET
    picture_url: str | Unset = UNSET
    github_username: str | Unset = UNSET
    website_url: str | Unset = UNSET
    twitter_username: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        bio = self.bio

        name = self.name

        picture_url = self.picture_url

        github_username = self.github_username

        website_url = self.website_url

        twitter_username = self.twitter_username


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if bio is not UNSET:
            field_dict["bio"] = bio
        if name is not UNSET:
            field_dict["name"] = name
        if picture_url is not UNSET:
            field_dict["pictureUrl"] = picture_url
        if github_username is not UNSET:
            field_dict["githubUsername"] = github_username
        if website_url is not UNSET:
            field_dict["websiteUrl"] = website_url
        if twitter_username is not UNSET:
            field_dict["twitterUsername"] = twitter_username

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        bio = d.pop("bio", UNSET)

        name = d.pop("name", UNSET)

        picture_url = d.pop("pictureUrl", UNSET)

        github_username = d.pop("githubUsername", UNSET)

        website_url = d.pop("websiteUrl", UNSET)

        twitter_username = d.pop("twitterUsername", UNSET)

        profile = cls(
            bio=bio,
            name=name,
            picture_url=picture_url,
            github_username=github_username,
            website_url=website_url,
            twitter_username=twitter_username,
        )


        profile.additional_properties = d
        return profile

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
