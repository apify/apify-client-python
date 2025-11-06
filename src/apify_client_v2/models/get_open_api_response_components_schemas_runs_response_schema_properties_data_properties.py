from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.get_open_api_response_components_schemas_runs_response_schema_properties_data_properties_status import GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesStatus
  from ..models.get_open_api_response_components_schemas_runs_response_schema_properties_data_properties_user_id import GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesUserId
  from ..models.get_open_api_response_components_schemas_runs_response_schema_properties_data_properties_started_at import GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesStartedAt
  from ..models.get_open_api_response_components_schemas_runs_response_schema_properties_data_properties_finished_at import GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesFinishedAt
  from ..models.get_open_api_response_components_schemas_runs_response_schema_properties_data_properties_act_id import GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesActId
  from ..models.get_open_api_response_components_schemas_runs_response_schema_properties_data_properties_id import GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesId
  from ..models.get_open_api_response_components_schemas_runs_response_schema_properties_data_properties_meta import GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesMeta





T = TypeVar("T", bound="GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataProperties")



@_attrs_define
class GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataProperties:
    """ 
        Attributes:
            id (GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesId | Unset):
            act_id (GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesActId | Unset):
            user_id (GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesUserId | Unset):
            started_at (GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesStartedAt | Unset):
            finished_at (GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesFinishedAt | Unset):
            status (GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesStatus | Unset):
            meta (GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesMeta | Unset):
     """

    id: GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesId | Unset = UNSET
    act_id: GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesActId | Unset = UNSET
    user_id: GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesUserId | Unset = UNSET
    started_at: GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesStartedAt | Unset = UNSET
    finished_at: GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesFinishedAt | Unset = UNSET
    status: GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesStatus | Unset = UNSET
    meta: GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesMeta | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.get_open_api_response_components_schemas_runs_response_schema_properties_data_properties_status import GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesStatus
        from ..models.get_open_api_response_components_schemas_runs_response_schema_properties_data_properties_user_id import GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesUserId
        from ..models.get_open_api_response_components_schemas_runs_response_schema_properties_data_properties_started_at import GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesStartedAt
        from ..models.get_open_api_response_components_schemas_runs_response_schema_properties_data_properties_finished_at import GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesFinishedAt
        from ..models.get_open_api_response_components_schemas_runs_response_schema_properties_data_properties_act_id import GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesActId
        from ..models.get_open_api_response_components_schemas_runs_response_schema_properties_data_properties_id import GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesId
        from ..models.get_open_api_response_components_schemas_runs_response_schema_properties_data_properties_meta import GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesMeta
        id: dict[str, Any] | Unset = UNSET
        if not isinstance(self.id, Unset):
            id = self.id.to_dict()

        act_id: dict[str, Any] | Unset = UNSET
        if not isinstance(self.act_id, Unset):
            act_id = self.act_id.to_dict()

        user_id: dict[str, Any] | Unset = UNSET
        if not isinstance(self.user_id, Unset):
            user_id = self.user_id.to_dict()

        started_at: dict[str, Any] | Unset = UNSET
        if not isinstance(self.started_at, Unset):
            started_at = self.started_at.to_dict()

        finished_at: dict[str, Any] | Unset = UNSET
        if not isinstance(self.finished_at, Unset):
            finished_at = self.finished_at.to_dict()

        status: dict[str, Any] | Unset = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.to_dict()

        meta: dict[str, Any] | Unset = UNSET
        if not isinstance(self.meta, Unset):
            meta = self.meta.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if id is not UNSET:
            field_dict["id"] = id
        if act_id is not UNSET:
            field_dict["actId"] = act_id
        if user_id is not UNSET:
            field_dict["userId"] = user_id
        if started_at is not UNSET:
            field_dict["startedAt"] = started_at
        if finished_at is not UNSET:
            field_dict["finishedAt"] = finished_at
        if status is not UNSET:
            field_dict["status"] = status
        if meta is not UNSET:
            field_dict["meta"] = meta

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_open_api_response_components_schemas_runs_response_schema_properties_data_properties_status import GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesStatus
        from ..models.get_open_api_response_components_schemas_runs_response_schema_properties_data_properties_user_id import GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesUserId
        from ..models.get_open_api_response_components_schemas_runs_response_schema_properties_data_properties_started_at import GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesStartedAt
        from ..models.get_open_api_response_components_schemas_runs_response_schema_properties_data_properties_finished_at import GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesFinishedAt
        from ..models.get_open_api_response_components_schemas_runs_response_schema_properties_data_properties_act_id import GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesActId
        from ..models.get_open_api_response_components_schemas_runs_response_schema_properties_data_properties_id import GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesId
        from ..models.get_open_api_response_components_schemas_runs_response_schema_properties_data_properties_meta import GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesMeta
        d = dict(src_dict)
        _id = d.pop("id", UNSET)
        id: GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesId | Unset
        if isinstance(_id,  Unset):
            id = UNSET
        else:
            id = GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesId.from_dict(_id)




        _act_id = d.pop("actId", UNSET)
        act_id: GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesActId | Unset
        if isinstance(_act_id,  Unset):
            act_id = UNSET
        else:
            act_id = GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesActId.from_dict(_act_id)




        _user_id = d.pop("userId", UNSET)
        user_id: GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesUserId | Unset
        if isinstance(_user_id,  Unset):
            user_id = UNSET
        else:
            user_id = GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesUserId.from_dict(_user_id)




        _started_at = d.pop("startedAt", UNSET)
        started_at: GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesStartedAt | Unset
        if isinstance(_started_at,  Unset):
            started_at = UNSET
        else:
            started_at = GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesStartedAt.from_dict(_started_at)




        _finished_at = d.pop("finishedAt", UNSET)
        finished_at: GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesFinishedAt | Unset
        if isinstance(_finished_at,  Unset):
            finished_at = UNSET
        else:
            finished_at = GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesFinishedAt.from_dict(_finished_at)




        _status = d.pop("status", UNSET)
        status: GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesStatus | Unset
        if isinstance(_status,  Unset):
            status = UNSET
        else:
            status = GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesStatus.from_dict(_status)




        _meta = d.pop("meta", UNSET)
        meta: GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesMeta | Unset
        if isinstance(_meta,  Unset):
            meta = UNSET
        else:
            meta = GetOpenApiResponseComponentsSchemasRunsResponseSchemaPropertiesDataPropertiesMeta.from_dict(_meta)




        get_open_api_response_components_schemas_runs_response_schema_properties_data_properties = cls(
            id=id,
            act_id=act_id,
            user_id=user_id,
            started_at=started_at,
            finished_at=finished_at,
            status=status,
            meta=meta,
        )


        get_open_api_response_components_schemas_runs_response_schema_properties_data_properties.additional_properties = d
        return get_open_api_response_components_schemas_runs_response_schema_properties_data_properties

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
