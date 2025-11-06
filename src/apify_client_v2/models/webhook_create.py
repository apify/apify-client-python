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





T = TypeVar("T", bound="WebhookCreate")



@_attrs_define
class WebhookCreate:
    r""" 
        Attributes:
            event_types (list[str]):  Example: ['ACTOR.RUN.SUCCEEDED'].
            condition (WebhookCondition):
            request_url (str):  Example: http://example.com/.
            is_ad_hoc (bool | None | Unset):
            idempotency_key (None | str | Unset):  Example: fdSJmdP3nfs7sfk3y.
            ignore_ssl_errors (bool | None | Unset):
            do_not_retry (bool | None | Unset):
            payload_template (None | str | Unset):  Example: {\n \"userId\": {{userId}}....
            headers_template (None | str | Unset):  Example: {\n \"Authorization\": Bearer....
            description (None | str | Unset):  Example: this is webhook description.
            should_interpolate_strings (bool | None | Unset):
     """

    event_types: list[str]
    condition: WebhookCondition
    request_url: str
    is_ad_hoc: bool | None | Unset = UNSET
    idempotency_key: None | str | Unset = UNSET
    ignore_ssl_errors: bool | None | Unset = UNSET
    do_not_retry: bool | None | Unset = UNSET
    payload_template: None | str | Unset = UNSET
    headers_template: None | str | Unset = UNSET
    description: None | str | Unset = UNSET
    should_interpolate_strings: bool | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.webhook_condition import WebhookCondition
        event_types = self.event_types



        condition = self.condition.to_dict()

        request_url = self.request_url

        is_ad_hoc: bool | None | Unset
        if isinstance(self.is_ad_hoc, Unset):
            is_ad_hoc = UNSET
        else:
            is_ad_hoc = self.is_ad_hoc

        idempotency_key: None | str | Unset
        if isinstance(self.idempotency_key, Unset):
            idempotency_key = UNSET
        else:
            idempotency_key = self.idempotency_key

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
            "eventTypes": event_types,
            "condition": condition,
            "requestUrl": request_url,
        })
        if is_ad_hoc is not UNSET:
            field_dict["isAdHoc"] = is_ad_hoc
        if idempotency_key is not UNSET:
            field_dict["idempotencyKey"] = idempotency_key
        if ignore_ssl_errors is not UNSET:
            field_dict["ignoreSslErrors"] = ignore_ssl_errors
        if do_not_retry is not UNSET:
            field_dict["doNotRetry"] = do_not_retry
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
        event_types = cast(list[str], d.pop("eventTypes"))


        condition = WebhookCondition.from_dict(d.pop("condition"))




        request_url = d.pop("requestUrl")

        def _parse_is_ad_hoc(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        is_ad_hoc = _parse_is_ad_hoc(d.pop("isAdHoc", UNSET))


        def _parse_idempotency_key(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        idempotency_key = _parse_idempotency_key(d.pop("idempotencyKey", UNSET))


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


        webhook_create = cls(
            event_types=event_types,
            condition=condition,
            request_url=request_url,
            is_ad_hoc=is_ad_hoc,
            idempotency_key=idempotency_key,
            ignore_ssl_errors=ignore_ssl_errors,
            do_not_retry=do_not_retry,
            payload_template=payload_template,
            headers_template=headers_template,
            description=description,
            should_interpolate_strings=should_interpolate_strings,
        )


        webhook_create.additional_properties = d
        return webhook_create

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
