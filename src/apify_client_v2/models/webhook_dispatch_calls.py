from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast






T = TypeVar("T", bound="WebhookDispatchCalls")



@_attrs_define
class WebhookDispatchCalls:
    """ 
        Attributes:
            started_at (None | str | Unset):  Example: 2019-12-12T07:34:14.202Z.
            finished_at (None | str | Unset):  Example: 2019-12-12T07:34:14.202Z.
            error_message (None | str | Unset):  Example: Cannot send request.
            response_status (float | None | Unset):  Example: 200.
            response_body (None | str | Unset):  Example: {'foo': 'bar'}.
     """

    started_at: None | str | Unset = UNSET
    finished_at: None | str | Unset = UNSET
    error_message: None | str | Unset = UNSET
    response_status: float | None | Unset = UNSET
    response_body: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        started_at: None | str | Unset
        if isinstance(self.started_at, Unset):
            started_at = UNSET
        else:
            started_at = self.started_at

        finished_at: None | str | Unset
        if isinstance(self.finished_at, Unset):
            finished_at = UNSET
        else:
            finished_at = self.finished_at

        error_message: None | str | Unset
        if isinstance(self.error_message, Unset):
            error_message = UNSET
        else:
            error_message = self.error_message

        response_status: float | None | Unset
        if isinstance(self.response_status, Unset):
            response_status = UNSET
        else:
            response_status = self.response_status

        response_body: None | str | Unset
        if isinstance(self.response_body, Unset):
            response_body = UNSET
        else:
            response_body = self.response_body


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if started_at is not UNSET:
            field_dict["startedAt"] = started_at
        if finished_at is not UNSET:
            field_dict["finishedAt"] = finished_at
        if error_message is not UNSET:
            field_dict["errorMessage"] = error_message
        if response_status is not UNSET:
            field_dict["responseStatus"] = response_status
        if response_body is not UNSET:
            field_dict["responseBody"] = response_body

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        def _parse_started_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        started_at = _parse_started_at(d.pop("startedAt", UNSET))


        def _parse_finished_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        finished_at = _parse_finished_at(d.pop("finishedAt", UNSET))


        def _parse_error_message(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        error_message = _parse_error_message(d.pop("errorMessage", UNSET))


        def _parse_response_status(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        response_status = _parse_response_status(d.pop("responseStatus", UNSET))


        def _parse_response_body(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        response_body = _parse_response_body(d.pop("responseBody", UNSET))


        webhook_dispatch_calls = cls(
            started_at=started_at,
            finished_at=finished_at,
            error_message=error_message,
            response_status=response_status,
            response_body=response_body,
        )


        webhook_dispatch_calls.additional_properties = d
        return webhook_dispatch_calls

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
