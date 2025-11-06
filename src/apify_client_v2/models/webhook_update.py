from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.webhook_condition import WebhookCondition





T = TypeVar("T", bound="WebhookUpdate")



@_attrs_define
class WebhookUpdate:
    r""" 
        Attributes:
            is_ad_hoc (bool | None | Unset):
            event_types (list[str] | None | Unset):  Example: ['ACTOR.RUN.SUCCEEDED'].
            condition (None | Unset | WebhookCondition):
            ignore_ssl_errors (bool | None | Unset):
            do_not_retry (bool | None | Unset):
            request_url (None | str | Unset):  Example: http://example.com/.
            payload_template (None | str | Unset):  Example: {\n \"userId\": {{userId}}....
            headers_template (None | str | Unset):  Example: {\n \"Authorization\": Bearer....
            description (None | str | Unset):  Example: this is webhook description.
            should_interpolate_strings (bool | None | Unset):
     """

    is_ad_hoc: bool | None | Unset = UNSET
    event_types: list[str] | None | Unset = UNSET
    condition: None | Unset | WebhookCondition = UNSET
    ignore_ssl_errors: bool | None | Unset = UNSET
    do_not_retry: bool | None | Unset = UNSET
    request_url: None | str | Unset = UNSET
    payload_template: None | str | Unset = UNSET
    headers_template: None | str | Unset = UNSET
    description: None | str | Unset = UNSET
    should_interpolate_strings: bool | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.webhook_condition import WebhookCondition
        is_ad_hoc: bool | None | Unset
        if isinstance(self.is_ad_hoc, Unset):
            is_ad_hoc = UNSET
        else:
            is_ad_hoc = self.is_ad_hoc

        event_types: list[str] | None | Unset
        if isinstance(self.event_types, Unset):
            event_types = UNSET
        elif isinstance(self.event_types, list):
            event_types = self.event_types


        else:
            event_types = self.event_types

        condition: dict[str, Any] | None | Unset
        if isinstance(self.condition, Unset):
            condition = UNSET
        elif isinstance(self.condition, WebhookCondition):
            condition = self.condition.to_dict()
        else:
            condition = self.condition

        ignore_ssl_errors: bool | None | Unset
        if isinstance(self.ignore_ssl_errors, Unset):
            ignore_ssl_errors = UNSET
        else:
            ignore_ssl_errors = self.ignore_ssl_errors

        do_not_retry: bool | None | Unset
        if isinstance(self.do_not_retry, Unset):
            do_not_retry = UNSET
        else:
            do_not_retry = self.do_not_retry

        request_url: None | str | Unset
        if isinstance(self.request_url, Unset):
            request_url = UNSET
        else:
            request_url = self.request_url

        payload_template: None | str | Unset
        if isinstance(self.payload_template, Unset):
            payload_template = UNSET
        else:
            payload_template = self.payload_template

        headers_template: None | str | Unset
        if isinstance(self.headers_template, Unset):
            headers_template = UNSET
        else:
            headers_template = self.headers_template

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        should_interpolate_strings: bool | None | Unset
        if isinstance(self.should_interpolate_strings, Unset):
            should_interpolate_strings = UNSET
        else:
            should_interpolate_strings = self.should_interpolate_strings


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if is_ad_hoc is not UNSET:
            field_dict["isAdHoc"] = is_ad_hoc
        if event_types is not UNSET:
            field_dict["eventTypes"] = event_types
        if condition is not UNSET:
            field_dict["condition"] = condition
        if ignore_ssl_errors is not UNSET:
            field_dict["ignoreSslErrors"] = ignore_ssl_errors
        if do_not_retry is not UNSET:
            field_dict["doNotRetry"] = do_not_retry
        if request_url is not UNSET:
            field_dict["requestUrl"] = request_url
        if payload_template is not UNSET:
            field_dict["payloadTemplate"] = payload_template
        if headers_template is not UNSET:
            field_dict["headersTemplate"] = headers_template
        if description is not UNSET:
            field_dict["description"] = description
        if should_interpolate_strings is not UNSET:
            field_dict["shouldInterpolateStrings"] = should_interpolate_strings

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.webhook_condition import WebhookCondition
        d = dict(src_dict)
        def _parse_is_ad_hoc(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        is_ad_hoc = _parse_is_ad_hoc(d.pop("isAdHoc", UNSET))


        def _parse_event_types(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                event_types_type_0 = cast(list[str], data)

                return event_types_type_0
            except: # noqa: E722
                pass
            return cast(list[str] | None | Unset, data)

        event_types = _parse_event_types(d.pop("eventTypes", UNSET))


        def _parse_condition(data: object) -> None | Unset | WebhookCondition:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                condition_type_1 = WebhookCondition.from_dict(data)



                return condition_type_1
            except: # noqa: E722
                pass
            return cast(None | Unset | WebhookCondition, data)

        condition = _parse_condition(d.pop("condition", UNSET))


        def _parse_ignore_ssl_errors(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        ignore_ssl_errors = _parse_ignore_ssl_errors(d.pop("ignoreSslErrors", UNSET))


        def _parse_do_not_retry(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        do_not_retry = _parse_do_not_retry(d.pop("doNotRetry", UNSET))


        def _parse_request_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        request_url = _parse_request_url(d.pop("requestUrl", UNSET))


        def _parse_payload_template(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        payload_template = _parse_payload_template(d.pop("payloadTemplate", UNSET))


        def _parse_headers_template(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        headers_template = _parse_headers_template(d.pop("headersTemplate", UNSET))


        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))


        def _parse_should_interpolate_strings(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        should_interpolate_strings = _parse_should_interpolate_strings(d.pop("shouldInterpolateStrings", UNSET))


        webhook_update = cls(
            is_ad_hoc=is_ad_hoc,
            event_types=event_types,
            condition=condition,
            ignore_ssl_errors=ignore_ssl_errors,
            do_not_retry=do_not_retry,
            request_url=request_url,
            payload_template=payload_template,
            headers_template=headers_template,
            description=description,
            should_interpolate_strings=should_interpolate_strings,
        )


        webhook_update.additional_properties = d
        return webhook_update

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
