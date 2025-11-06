from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast






T = TypeVar("T", bound="EffectivePlatformFeature")



@_attrs_define
class EffectivePlatformFeature:
    """ 
        Attributes:
            is_enabled (bool):  Example: True.
            disabled_reason (None | str):  Example: The "Selected public Actors for developers" feature is not enabled for
                your account. Please upgrade your plan or contact support@apify.com.
            disabled_reason_type (None | str):  Example: DISABLED.
            is_trial (bool):
            trial_expiration_at (None | str):  Example: 2025-01-01T14:00:00.000Z.
     """

    is_enabled: bool
    disabled_reason: None | str
    disabled_reason_type: None | str
    is_trial: bool
    trial_expiration_at: None | str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        is_enabled = self.is_enabled

        disabled_reason: None | str
        disabled_reason = self.disabled_reason

        disabled_reason_type: None | str
        disabled_reason_type = self.disabled_reason_type

        is_trial = self.is_trial

        trial_expiration_at: None | str
        trial_expiration_at = self.trial_expiration_at


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "isEnabled": is_enabled,
            "disabledReason": disabled_reason,
            "disabledReasonType": disabled_reason_type,
            "isTrial": is_trial,
            "trialExpirationAt": trial_expiration_at,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        is_enabled = d.pop("isEnabled")

        def _parse_disabled_reason(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        disabled_reason = _parse_disabled_reason(d.pop("disabledReason"))


        def _parse_disabled_reason_type(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        disabled_reason_type = _parse_disabled_reason_type(d.pop("disabledReasonType"))


        is_trial = d.pop("isTrial")

        def _parse_trial_expiration_at(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        trial_expiration_at = _parse_trial_expiration_at(d.pop("trialExpirationAt"))


        effective_platform_feature = cls(
            is_enabled=is_enabled,
            disabled_reason=disabled_reason,
            disabled_reason_type=disabled_reason_type,
            is_trial=is_trial,
            trial_expiration_at=trial_expiration_at,
        )


        effective_platform_feature.additional_properties = d
        return effective_platform_feature

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
