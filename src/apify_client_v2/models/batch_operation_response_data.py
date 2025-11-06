from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
  from ..models.unprocessed_request import UnprocessedRequest
  from ..models.processed_request import ProcessedRequest





T = TypeVar("T", bound="BatchOperationResponseData")



@_attrs_define
class BatchOperationResponseData:
    """ 
        Attributes:
            processed_requests (list[ProcessedRequest]):
            unprocessed_requests (list[UnprocessedRequest]):
     """

    processed_requests: list[ProcessedRequest]
    unprocessed_requests: list[UnprocessedRequest]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.unprocessed_request import UnprocessedRequest
        from ..models.processed_request import ProcessedRequest
        processed_requests = []
        for processed_requests_item_data in self.processed_requests:
            processed_requests_item = processed_requests_item_data.to_dict()
            processed_requests.append(processed_requests_item)



        unprocessed_requests = []
        for unprocessed_requests_item_data in self.unprocessed_requests:
            unprocessed_requests_item = unprocessed_requests_item_data.to_dict()
            unprocessed_requests.append(unprocessed_requests_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "processedRequests": processed_requests,
            "unprocessedRequests": unprocessed_requests,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.unprocessed_request import UnprocessedRequest
        from ..models.processed_request import ProcessedRequest
        d = dict(src_dict)
        processed_requests = []
        _processed_requests = d.pop("processedRequests")
        for processed_requests_item_data in (_processed_requests):
            processed_requests_item = ProcessedRequest.from_dict(processed_requests_item_data)



            processed_requests.append(processed_requests_item)


        unprocessed_requests = []
        _unprocessed_requests = d.pop("unprocessedRequests")
        for unprocessed_requests_item_data in (_unprocessed_requests):
            unprocessed_requests_item = UnprocessedRequest.from_dict(unprocessed_requests_item_data)



            unprocessed_requests.append(unprocessed_requests_item)


        batch_operation_response_data = cls(
            processed_requests=processed_requests,
            unprocessed_requests=unprocessed_requests,
        )


        batch_operation_response_data.additional_properties = d
        return batch_operation_response_data

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
