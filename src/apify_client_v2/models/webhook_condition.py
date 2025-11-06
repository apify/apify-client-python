from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast






T = TypeVar("T", bound="WebhookCondition")



@_attrs_define
class WebhookCondition:
    """ 
        Attributes:
            actor_id (None | str | Unset):  Example: hksJZtadYvn4mBuin.
            actor_task_id (None | str | Unset):  Example: asdLZtadYvn4mBZmm.
            actor_run_id (None | str | Unset):  Example: hgdKZtadYvn4mBpoi.
     """

    actor_id: None | str | Unset = UNSET
    actor_task_id: None | str | Unset = UNSET
    actor_run_id: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        actor_id: None | str | Unset
        if isinstance(self.actor_id, Unset):
            actor_id = UNSET
        else:
            actor_id = self.actor_id

        actor_task_id: None | str | Unset
        if isinstance(self.actor_task_id, Unset):
            actor_task_id = UNSET
        else:
            actor_task_id = self.actor_task_id

        actor_run_id: None | str | Unset
        if isinstance(self.actor_run_id, Unset):
            actor_run_id = UNSET
        else:
            actor_run_id = self.actor_run_id


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if actor_id is not UNSET:
            field_dict["actorId"] = actor_id
        if actor_task_id is not UNSET:
            field_dict["actorTaskId"] = actor_task_id
        if actor_run_id is not UNSET:
            field_dict["actorRunId"] = actor_run_id

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        def _parse_actor_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        actor_id = _parse_actor_id(d.pop("actorId", UNSET))


        def _parse_actor_task_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        actor_task_id = _parse_actor_task_id(d.pop("actorTaskId", UNSET))


        def _parse_actor_run_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        actor_run_id = _parse_actor_run_id(d.pop("actorRunId", UNSET))


        webhook_condition = cls(
            actor_id=actor_id,
            actor_task_id=actor_task_id,
            actor_run_id=actor_run_id,
        )


        webhook_condition.additional_properties = d
        return webhook_condition

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
