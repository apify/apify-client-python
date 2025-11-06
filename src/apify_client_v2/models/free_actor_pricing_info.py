from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.free_actor_pricing_info_pricing_model import FreeActorPricingInfoPricingModel
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
import datetime






T = TypeVar("T", bound="FreeActorPricingInfo")



@_attrs_define
class FreeActorPricingInfo:
    """ 
        Attributes:
            apify_margin_percentage (float): In [0, 1], fraction of pricePerUnitUsd that goes to Apify
            created_at (datetime.datetime): When this pricing info record has been created
            started_at (datetime.datetime): Since when is this pricing info record effective for a given Actor
            pricing_model (FreeActorPricingInfoPricingModel):
            notified_about_future_change_at (datetime.datetime | None | Unset):
            notified_about_change_at (datetime.datetime | None | Unset):
            reason_for_change (None | str | Unset):
     """

    apify_margin_percentage: float
    created_at: datetime.datetime
    started_at: datetime.datetime
    pricing_model: FreeActorPricingInfoPricingModel
    notified_about_future_change_at: datetime.datetime | None | Unset = UNSET
    notified_about_change_at: datetime.datetime | None | Unset = UNSET
    reason_for_change: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        apify_margin_percentage = self.apify_margin_percentage

        created_at = self.created_at.isoformat()

        started_at = self.started_at.isoformat()

        pricing_model = self.pricing_model.value

        notified_about_future_change_at: None | str | Unset
        if isinstance(self.notified_about_future_change_at, Unset):
            notified_about_future_change_at = UNSET
        elif isinstance(self.notified_about_future_change_at, datetime.datetime):
            notified_about_future_change_at = self.notified_about_future_change_at.isoformat()
        else:
            notified_about_future_change_at = self.notified_about_future_change_at

        notified_about_change_at: None | str | Unset
        if isinstance(self.notified_about_change_at, Unset):
            notified_about_change_at = UNSET
        elif isinstance(self.notified_about_change_at, datetime.datetime):
            notified_about_change_at = self.notified_about_change_at.isoformat()
        else:
            notified_about_change_at = self.notified_about_change_at

        reason_for_change: None | str | Unset
        if isinstance(self.reason_for_change, Unset):
            reason_for_change = UNSET
        else:
            reason_for_change = self.reason_for_change


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "apifyMarginPercentage": apify_margin_percentage,
            "createdAt": created_at,
            "startedAt": started_at,
            "pricingModel": pricing_model,
        })
        if notified_about_future_change_at is not UNSET:
            field_dict["notifiedAboutFutureChangeAt"] = notified_about_future_change_at
        if notified_about_change_at is not UNSET:
            field_dict["notifiedAboutChangeAt"] = notified_about_change_at
        if reason_for_change is not UNSET:
            field_dict["reasonForChange"] = reason_for_change

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        apify_margin_percentage = d.pop("apifyMarginPercentage")

        created_at = isoparse(d.pop("createdAt"))




        started_at = isoparse(d.pop("startedAt"))




        pricing_model = FreeActorPricingInfoPricingModel(d.pop("pricingModel"))




        def _parse_notified_about_future_change_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                notified_about_future_change_at_type_0 = isoparse(data)



                return notified_about_future_change_at_type_0
            except: # noqa: E722
                pass
            return cast(datetime.datetime | None | Unset, data)

        notified_about_future_change_at = _parse_notified_about_future_change_at(d.pop("notifiedAboutFutureChangeAt", UNSET))


        def _parse_notified_about_change_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                notified_about_change_at_type_0 = isoparse(data)



                return notified_about_change_at_type_0
            except: # noqa: E722
                pass
            return cast(datetime.datetime | None | Unset, data)

        notified_about_change_at = _parse_notified_about_change_at(d.pop("notifiedAboutChangeAt", UNSET))


        def _parse_reason_for_change(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        reason_for_change = _parse_reason_for_change(d.pop("reasonForChange", UNSET))


        free_actor_pricing_info = cls(
            apify_margin_percentage=apify_margin_percentage,
            created_at=created_at,
            started_at=started_at,
            pricing_model=pricing_model,
            notified_about_future_change_at=notified_about_future_change_at,
            notified_about_change_at=notified_about_change_at,
            reason_for_change=reason_for_change,
        )


        free_actor_pricing_info.additional_properties = d
        return free_actor_pricing_info

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
