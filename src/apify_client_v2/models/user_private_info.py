from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
  from ..models.effective_platform_features import EffectivePlatformFeatures
  from ..models.plan import Plan
  from ..models.proxy import Proxy
  from ..models.profile import Profile





T = TypeVar("T", bound="UserPrivateInfo")



@_attrs_define
class UserPrivateInfo:
    """ 
        Attributes:
            id (str):  Example: YiKoxjkaS9gjGTqhF.
            username (str):  Example: myusername.
            profile (Profile):
            email (str):  Example: bob@example.com.
            proxy (Proxy):
            plan (Plan):
            effective_platform_features (EffectivePlatformFeatures):
            created_at (str):  Example: 2022-11-29T14:48:29.381Z.
            is_paying (bool):  Example: True.
     """

    id: str
    username: str
    profile: Profile
    email: str
    proxy: Proxy
    plan: Plan
    effective_platform_features: EffectivePlatformFeatures
    created_at: str
    is_paying: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.effective_platform_features import EffectivePlatformFeatures
        from ..models.plan import Plan
        from ..models.proxy import Proxy
        from ..models.profile import Profile
        id = self.id

        username = self.username

        profile = self.profile.to_dict()

        email = self.email

        proxy = self.proxy.to_dict()

        plan = self.plan.to_dict()

        effective_platform_features = self.effective_platform_features.to_dict()

        created_at = self.created_at

        is_paying = self.is_paying


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "username": username,
            "profile": profile,
            "email": email,
            "proxy": proxy,
            "plan": plan,
            "effectivePlatformFeatures": effective_platform_features,
            "createdAt": created_at,
            "isPaying": is_paying,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.effective_platform_features import EffectivePlatformFeatures
        from ..models.plan import Plan
        from ..models.proxy import Proxy
        from ..models.profile import Profile
        d = dict(src_dict)
        id = d.pop("id")

        username = d.pop("username")

        profile = Profile.from_dict(d.pop("profile"))




        email = d.pop("email")

        proxy = Proxy.from_dict(d.pop("proxy"))




        plan = Plan.from_dict(d.pop("plan"))




        effective_platform_features = EffectivePlatformFeatures.from_dict(d.pop("effectivePlatformFeatures"))




        created_at = d.pop("createdAt")

        is_paying = d.pop("isPaying")

        user_private_info = cls(
            id=id,
            username=username,
            profile=profile,
            email=email,
            proxy=proxy,
            plan=plan,
            effective_platform_features=effective_platform_features,
            created_at=created_at,
            is_paying=is_paying,
        )


        user_private_info.additional_properties = d
        return user_private_info

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
