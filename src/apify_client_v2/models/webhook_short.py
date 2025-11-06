from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.webhook_stats import WebhookStats
  from ..models.webhook_condition import WebhookCondition
  from ..models.example_webhook_dispatch import ExampleWebhookDispatch





T = TypeVar("T", bound="WebhookShort")



@_attrs_define
class WebhookShort:
    """ 
        Attributes:
            id (str):  Example: YiKoxjkaS9gjGTqhF.
            created_at (str):  Example: 2019-12-12T07:34:14.202Z.
            modified_at (str):  Example: 2019-12-13T08:36:13.202Z.
            user_id (str):  Example: wRsJZtadYvn4mBZmm.
            event_types (list[str]):  Example: ['ACTOR.RUN.SUCCEEDED'].
            condition (WebhookCondition):
            ignore_ssl_errors (bool):
            do_not_retry (bool):
            request_url (str):  Example: http://example.com/.
            is_ad_hoc (bool | None | Unset):
            should_interpolate_strings (bool | None | Unset):
            last_dispatch (ExampleWebhookDispatch | None | Unset):
            stats (None | Unset | WebhookStats):
     """

    id: str
    created_at: str
    modified_at: str
    user_id: str
    event_types: list[str]
    condition: WebhookCondition
    ignore_ssl_errors: bool
    do_not_retry: bool
    request_url: str
    is_ad_hoc: bool | None | Unset = UNSET
    should_interpolate_strings: bool | None | Unset = UNSET
    last_dispatch: ExampleWebhookDispatch | None | Unset = UNSET
    stats: None | Unset | WebhookStats = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.webhook_stats import WebhookStats
        from ..models.webhook_condition import WebhookCondition
        from ..models.example_webhook_dispatch import ExampleWebhookDispatch
        id = self.id

        created_at = self.created_at

        modified_at = self.modified_at

        user_id = self.user_id

        event_types = self.event_types



        condition = self.condition.to_dict()

        ignore_ssl_errors = self.ignore_ssl_errors

        do_not_retry = self.do_not_retry

        request_url = self.request_url

        is_ad_hoc: bool | None | Unset
        if isinstance(self.is_ad_hoc, Unset):
            is_ad_hoc = UNSET
        else:
            is_ad_hoc = self.is_ad_hoc

        should_interpolate_strings: bool | None | Unset
        if isinstance(self.should_interpolate_strings, Unset):
            should_interpolate_strings = UNSET
        else:
            should_interpolate_strings = self.should_interpolate_strings

        last_dispatch: dict[str, Any] | None | Unset
        if isinstance(self.last_dispatch, Unset):
            last_dispatch = UNSET
        elif isinstance(self.last_dispatch, ExampleWebhookDispatch):
            last_dispatch = self.last_dispatch.to_dict()
        else:
            last_dispatch = self.last_dispatch

        stats: dict[str, Any] | None | Unset
        if isinstance(self.stats, Unset):
            stats = UNSET
        elif isinstance(self.stats, WebhookStats):
            stats = self.stats.to_dict()
        else:
            stats = self.stats


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "createdAt": created_at,
            "modifiedAt": modified_at,
            "userId": user_id,
            "eventTypes": event_types,
            "condition": condition,
            "ignoreSslErrors": ignore_ssl_errors,
            "doNotRetry": do_not_retry,
            "requestUrl": request_url,
        })
        if is_ad_hoc is not UNSET:
            field_dict["isAdHoc"] = is_ad_hoc
        if should_interpolate_strings is not UNSET:
            field_dict["shouldInterpolateStrings"] = should_interpolate_strings
        if last_dispatch is not UNSET:
            field_dict["lastDispatch"] = last_dispatch
        if stats is not UNSET:
            field_dict["stats"] = stats

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.webhook_stats import WebhookStats
        from ..models.webhook_condition import WebhookCondition
        from ..models.example_webhook_dispatch import ExampleWebhookDispatch
        d = dict(src_dict)
        id = d.pop("id")

        created_at = d.pop("createdAt")

        modified_at = d.pop("modifiedAt")

        user_id = d.pop("userId")

        event_types = cast(list[str], d.pop("eventTypes"))


        condition = WebhookCondition.from_dict(d.pop("condition"))




        ignore_ssl_errors = d.pop("ignoreSslErrors")

        do_not_retry = d.pop("doNotRetry")

        request_url = d.pop("requestUrl")

        def _parse_is_ad_hoc(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        is_ad_hoc = _parse_is_ad_hoc(d.pop("isAdHoc", UNSET))


        def _parse_should_interpolate_strings(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        should_interpolate_strings = _parse_should_interpolate_strings(d.pop("shouldInterpolateStrings", UNSET))


        def _parse_last_dispatch(data: object) -> ExampleWebhookDispatch | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                last_dispatch_type_1 = ExampleWebhookDispatch.from_dict(data)



                return last_dispatch_type_1
            except: # noqa: E722
                pass
            return cast(ExampleWebhookDispatch | None | Unset, data)

        last_dispatch = _parse_last_dispatch(d.pop("lastDispatch", UNSET))


        def _parse_stats(data: object) -> None | Unset | WebhookStats:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                stats_type_1 = WebhookStats.from_dict(data)



                return stats_type_1
            except: # noqa: E722
                pass
            return cast(None | Unset | WebhookStats, data)

        stats = _parse_stats(d.pop("stats", UNSET))


        webhook_short = cls(
            id=id,
            created_at=created_at,
            modified_at=modified_at,
            user_id=user_id,
            event_types=event_types,
            condition=condition,
            ignore_ssl_errors=ignore_ssl_errors,
            do_not_retry=do_not_retry,
            request_url=request_url,
            is_ad_hoc=is_ad_hoc,
            should_interpolate_strings=should_interpolate_strings,
            last_dispatch=last_dispatch,
            stats=stats,
        )


        webhook_short.additional_properties = d
        return webhook_short

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
