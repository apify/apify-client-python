from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.request_queue_items_payload_type_0 import RequestQueueItemsPayloadType0
  from ..models.request_queue_items_user_data import RequestQueueItemsUserData
  from ..models.request_queue_items_headers_type_0 import RequestQueueItemsHeadersType0





T = TypeVar("T", bound="GetRequestResponseData")



@_attrs_define
class GetRequestResponseData:
    """ 
        Attributes:
            id (str):  Example: dnjkDMKLmdlkmlkmld.
            retry_count (float):
            unique_key (str):  Example: http://example.com.
            url (str):  Example: http://example.com.
            method (str):  Example: GET.
            loaded_url (None | str | Unset):  Example: http://example.com/example-1.
            payload (None | RequestQueueItemsPayloadType0 | Unset):
            no_retry (bool | None | Unset):
            error_messages (list[str] | None | Unset):
            headers (None | RequestQueueItemsHeadersType0 | Unset):
            user_data (RequestQueueItemsUserData | Unset):
            handled_at (None | str | Unset):  Example: 2019-06-16T10:23:31.607Z.
     """

    id: str
    retry_count: float
    unique_key: str
    url: str
    method: str
    loaded_url: None | str | Unset = UNSET
    payload: None | RequestQueueItemsPayloadType0 | Unset = UNSET
    no_retry: bool | None | Unset = UNSET
    error_messages: list[str] | None | Unset = UNSET
    headers: None | RequestQueueItemsHeadersType0 | Unset = UNSET
    user_data: RequestQueueItemsUserData | Unset = UNSET
    handled_at: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.request_queue_items_payload_type_0 import RequestQueueItemsPayloadType0
        from ..models.request_queue_items_user_data import RequestQueueItemsUserData
        from ..models.request_queue_items_headers_type_0 import RequestQueueItemsHeadersType0
        id = self.id

        retry_count = self.retry_count

        unique_key = self.unique_key

        url = self.url

        method = self.method

        loaded_url: None | str | Unset
        if isinstance(self.loaded_url, Unset):
            loaded_url = UNSET
        else:
            loaded_url = self.loaded_url

        payload: dict[str, Any] | None | Unset
        if isinstance(self.payload, Unset):
            payload = UNSET
        elif isinstance(self.payload, RequestQueueItemsPayloadType0):
            payload = self.payload.to_dict()
        else:
            payload = self.payload

        no_retry: bool | None | Unset
        if isinstance(self.no_retry, Unset):
            no_retry = UNSET
        else:
            no_retry = self.no_retry

        error_messages: list[str] | None | Unset
        if isinstance(self.error_messages, Unset):
            error_messages = UNSET
        elif isinstance(self.error_messages, list):
            error_messages = self.error_messages


        else:
            error_messages = self.error_messages

        headers: dict[str, Any] | None | Unset
        if isinstance(self.headers, Unset):
            headers = UNSET
        elif isinstance(self.headers, RequestQueueItemsHeadersType0):
            headers = self.headers.to_dict()
        else:
            headers = self.headers

        user_data: dict[str, Any] | Unset = UNSET
        if not isinstance(self.user_data, Unset):
            user_data = self.user_data.to_dict()

        handled_at: None | str | Unset
        if isinstance(self.handled_at, Unset):
            handled_at = UNSET
        else:
            handled_at = self.handled_at


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "retryCount": retry_count,
            "uniqueKey": unique_key,
            "url": url,
            "method": method,
        })
        if loaded_url is not UNSET:
            field_dict["loadedUrl"] = loaded_url
        if payload is not UNSET:
            field_dict["payload"] = payload
        if no_retry is not UNSET:
            field_dict["noRetry"] = no_retry
        if error_messages is not UNSET:
            field_dict["errorMessages"] = error_messages
        if headers is not UNSET:
            field_dict["headers"] = headers
        if user_data is not UNSET:
            field_dict["userData"] = user_data
        if handled_at is not UNSET:
            field_dict["handledAt"] = handled_at

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.request_queue_items_payload_type_0 import RequestQueueItemsPayloadType0
        from ..models.request_queue_items_user_data import RequestQueueItemsUserData
        from ..models.request_queue_items_headers_type_0 import RequestQueueItemsHeadersType0
        d = dict(src_dict)
        id = d.pop("id")

        retry_count = d.pop("retryCount")

        unique_key = d.pop("uniqueKey")

        url = d.pop("url")

        method = d.pop("method")

        def _parse_loaded_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        loaded_url = _parse_loaded_url(d.pop("loadedUrl", UNSET))


        def _parse_payload(data: object) -> None | RequestQueueItemsPayloadType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                payload_type_0 = RequestQueueItemsPayloadType0.from_dict(data)



                return payload_type_0
            except: # noqa: E722
                pass
            return cast(None | RequestQueueItemsPayloadType0 | Unset, data)

        payload = _parse_payload(d.pop("payload", UNSET))


        def _parse_no_retry(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        no_retry = _parse_no_retry(d.pop("noRetry", UNSET))


        def _parse_error_messages(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                error_messages_type_0 = cast(list[str], data)

                return error_messages_type_0
            except: # noqa: E722
                pass
            return cast(list[str] | None | Unset, data)

        error_messages = _parse_error_messages(d.pop("errorMessages", UNSET))


        def _parse_headers(data: object) -> None | RequestQueueItemsHeadersType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                headers_type_0 = RequestQueueItemsHeadersType0.from_dict(data)



                return headers_type_0
            except: # noqa: E722
                pass
            return cast(None | RequestQueueItemsHeadersType0 | Unset, data)

        headers = _parse_headers(d.pop("headers", UNSET))


        _user_data = d.pop("userData", UNSET)
        user_data: RequestQueueItemsUserData | Unset
        if isinstance(_user_data,  Unset):
            user_data = UNSET
        else:
            user_data = RequestQueueItemsUserData.from_dict(_user_data)




        def _parse_handled_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        handled_at = _parse_handled_at(d.pop("handledAt", UNSET))


        get_request_response_data = cls(
            id=id,
            retry_count=retry_count,
            unique_key=unique_key,
            url=url,
            method=method,
            loaded_url=loaded_url,
            payload=payload,
            no_retry=no_retry,
            error_messages=error_messages,
            headers=headers,
            user_data=user_data,
            handled_at=handled_at,
        )


        get_request_response_data.additional_properties = d
        return get_request_response_data

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
