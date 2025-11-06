from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.get_open_api_response_paths_actsusernameactorrun_sync_get_dataset_items_post_parameters_item import GetOpenApiResponsePathsActsusernameactorrunSyncGetDatasetItemsPostParametersItem
  from ..models.get_open_api_response_paths_actsusernameactorrun_sync_get_dataset_items_post_responses import GetOpenApiResponsePathsActsusernameactorrunSyncGetDatasetItemsPostResponses
  from ..models.get_open_api_response_paths_actsusernameactorrun_sync_get_dataset_items_post_request_body import GetOpenApiResponsePathsActsusernameactorrunSyncGetDatasetItemsPostRequestBody





T = TypeVar("T", bound="GetOpenApiResponsePathsActsusernameactorrunSyncGetDatasetItemsPost")



@_attrs_define
class GetOpenApiResponsePathsActsusernameactorrunSyncGetDatasetItemsPost:
    """ 
        Attributes:
            operation_id (str | Unset):  Example: run-sync-get-dataset-items.
            x_openai_is_consequential (bool | Unset):
            summary (str | Unset):  Example: Executes an Actor, waits for its completion, and returns Actor's dataset items
                in response..
            tags (list[str] | Unset):  Example: ['Run Actor'].
            request_body (GetOpenApiResponsePathsActsusernameactorrunSyncGetDatasetItemsPostRequestBody | Unset):
            parameters (list[GetOpenApiResponsePathsActsusernameactorrunSyncGetDatasetItemsPostParametersItem] | Unset):
            responses (GetOpenApiResponsePathsActsusernameactorrunSyncGetDatasetItemsPostResponses | Unset):
     """

    operation_id: str | Unset = UNSET
    x_openai_is_consequential: bool | Unset = UNSET
    summary: str | Unset = UNSET
    tags: list[str] | Unset = UNSET
    request_body: GetOpenApiResponsePathsActsusernameactorrunSyncGetDatasetItemsPostRequestBody | Unset = UNSET
    parameters: list[GetOpenApiResponsePathsActsusernameactorrunSyncGetDatasetItemsPostParametersItem] | Unset = UNSET
    responses: GetOpenApiResponsePathsActsusernameactorrunSyncGetDatasetItemsPostResponses | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.get_open_api_response_paths_actsusernameactorrun_sync_get_dataset_items_post_parameters_item import GetOpenApiResponsePathsActsusernameactorrunSyncGetDatasetItemsPostParametersItem
        from ..models.get_open_api_response_paths_actsusernameactorrun_sync_get_dataset_items_post_responses import GetOpenApiResponsePathsActsusernameactorrunSyncGetDatasetItemsPostResponses
        from ..models.get_open_api_response_paths_actsusernameactorrun_sync_get_dataset_items_post_request_body import GetOpenApiResponsePathsActsusernameactorrunSyncGetDatasetItemsPostRequestBody
        operation_id = self.operation_id

        x_openai_is_consequential = self.x_openai_is_consequential

        summary = self.summary

        tags: list[str] | Unset = UNSET
        if not isinstance(self.tags, Unset):
            tags = self.tags



        request_body: dict[str, Any] | Unset = UNSET
        if not isinstance(self.request_body, Unset):
            request_body = self.request_body.to_dict()

        parameters: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.parameters, Unset):
            parameters = []
            for parameters_item_data in self.parameters:
                parameters_item = parameters_item_data.to_dict()
                parameters.append(parameters_item)



        responses: dict[str, Any] | Unset = UNSET
        if not isinstance(self.responses, Unset):
            responses = self.responses.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if operation_id is not UNSET:
            field_dict["operationId"] = operation_id
        if x_openai_is_consequential is not UNSET:
            field_dict["x-openai-isConsequential"] = x_openai_is_consequential
        if summary is not UNSET:
            field_dict["summary"] = summary
        if tags is not UNSET:
            field_dict["tags"] = tags
        if request_body is not UNSET:
            field_dict["requestBody"] = request_body
        if parameters is not UNSET:
            field_dict["parameters"] = parameters
        if responses is not UNSET:
            field_dict["responses"] = responses

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_open_api_response_paths_actsusernameactorrun_sync_get_dataset_items_post_parameters_item import GetOpenApiResponsePathsActsusernameactorrunSyncGetDatasetItemsPostParametersItem
        from ..models.get_open_api_response_paths_actsusernameactorrun_sync_get_dataset_items_post_responses import GetOpenApiResponsePathsActsusernameactorrunSyncGetDatasetItemsPostResponses
        from ..models.get_open_api_response_paths_actsusernameactorrun_sync_get_dataset_items_post_request_body import GetOpenApiResponsePathsActsusernameactorrunSyncGetDatasetItemsPostRequestBody
        d = dict(src_dict)
        operation_id = d.pop("operationId", UNSET)

        x_openai_is_consequential = d.pop("x-openai-isConsequential", UNSET)

        summary = d.pop("summary", UNSET)

        tags = cast(list[str], d.pop("tags", UNSET))


        _request_body = d.pop("requestBody", UNSET)
        request_body: GetOpenApiResponsePathsActsusernameactorrunSyncGetDatasetItemsPostRequestBody | Unset
        if isinstance(_request_body,  Unset):
            request_body = UNSET
        else:
            request_body = GetOpenApiResponsePathsActsusernameactorrunSyncGetDatasetItemsPostRequestBody.from_dict(_request_body)




        parameters = []
        _parameters = d.pop("parameters", UNSET)
        for parameters_item_data in (_parameters or []):
            parameters_item = GetOpenApiResponsePathsActsusernameactorrunSyncGetDatasetItemsPostParametersItem.from_dict(parameters_item_data)



            parameters.append(parameters_item)


        _responses = d.pop("responses", UNSET)
        responses: GetOpenApiResponsePathsActsusernameactorrunSyncGetDatasetItemsPostResponses | Unset
        if isinstance(_responses,  Unset):
            responses = UNSET
        else:
            responses = GetOpenApiResponsePathsActsusernameactorrunSyncGetDatasetItemsPostResponses.from_dict(_responses)




        get_open_api_response_paths_actsusernameactorrun_sync_get_dataset_items_post = cls(
            operation_id=operation_id,
            x_openai_is_consequential=x_openai_is_consequential,
            summary=summary,
            tags=tags,
            request_body=request_body,
            parameters=parameters,
            responses=responses,
        )


        get_open_api_response_paths_actsusernameactorrun_sync_get_dataset_items_post.additional_properties = d
        return get_open_api_response_paths_actsusernameactorrun_sync_get_dataset_items_post

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
