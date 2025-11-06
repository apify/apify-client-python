from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.run_short_meta import RunShortMeta





T = TypeVar("T", bound="RunShort")



@_attrs_define
class RunShort:
    """ 
        Attributes:
            id (str):  Example: HG7ML7M8z78YcAPEB.
            act_id (str):  Example: HDSasDasz78YcAPEB.
            status (str):  Example: SUCCEEDED.
            started_at (str):  Example: 2019-11-30T07:34:24.202Z.
            finished_at (str):  Example: 2019-12-12T09:30:12.202Z.
            build_id (str):  Example: HG7ML7M8z78YcAPEB.
            build_number (str):  Example: 0.0.2.
            meta (RunShortMeta):
            usage_total_usd (float):  Example: 0.2.
            default_key_value_store_id (str):  Example: sfAjeR4QmeJCQzTfe.
            default_dataset_id (str):  Example: 3ZojQDdFTsyE7Moy4.
            default_request_queue_id (str):  Example: so93g2shcDzK3pA85.
            actor_task_id (None | str | Unset):  Example: KJHSKHausidyaJKHs.
     """

    id: str
    act_id: str
    status: str
    started_at: str
    finished_at: str
    build_id: str
    build_number: str
    meta: RunShortMeta
    usage_total_usd: float
    default_key_value_store_id: str
    default_dataset_id: str
    default_request_queue_id: str
    actor_task_id: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.run_short_meta import RunShortMeta
        id = self.id

        act_id = self.act_id

        status = self.status

        started_at = self.started_at

        finished_at = self.finished_at

        build_id = self.build_id

        build_number = self.build_number

        meta = self.meta.to_dict()

        usage_total_usd = self.usage_total_usd

        default_key_value_store_id = self.default_key_value_store_id

        default_dataset_id = self.default_dataset_id

        default_request_queue_id = self.default_request_queue_id

        actor_task_id: None | str | Unset
        if isinstance(self.actor_task_id, Unset):
            actor_task_id = UNSET
        else:
            actor_task_id = self.actor_task_id


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "actId": act_id,
            "status": status,
            "startedAt": started_at,
            "finishedAt": finished_at,
            "buildId": build_id,
            "buildNumber": build_number,
            "meta": meta,
            "usageTotalUsd": usage_total_usd,
            "defaultKeyValueStoreId": default_key_value_store_id,
            "defaultDatasetId": default_dataset_id,
            "defaultRequestQueueId": default_request_queue_id,
        })
        if actor_task_id is not UNSET:
            field_dict["actorTaskId"] = actor_task_id

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.run_short_meta import RunShortMeta
        d = dict(src_dict)
        id = d.pop("id")

        act_id = d.pop("actId")

        status = d.pop("status")

        started_at = d.pop("startedAt")

        finished_at = d.pop("finishedAt")

        build_id = d.pop("buildId")

        build_number = d.pop("buildNumber")

        meta = RunShortMeta.from_dict(d.pop("meta"))




        usage_total_usd = d.pop("usageTotalUsd")

        default_key_value_store_id = d.pop("defaultKeyValueStoreId")

        default_dataset_id = d.pop("defaultDatasetId")

        default_request_queue_id = d.pop("defaultRequestQueueId")

        def _parse_actor_task_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        actor_task_id = _parse_actor_task_id(d.pop("actorTaskId", UNSET))


        run_short = cls(
            id=id,
            act_id=act_id,
            status=status,
            started_at=started_at,
            finished_at=finished_at,
            build_id=build_id,
            build_number=build_number,
            meta=meta,
            usage_total_usd=usage_total_usd,
            default_key_value_store_id=default_key_value_store_id,
            default_dataset_id=default_dataset_id,
            default_request_queue_id=default_request_queue_id,
            actor_task_id=actor_task_id,
        )


        run_short.additional_properties = d
        return run_short

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
