from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.task_short_stats import TaskShortStats





T = TypeVar("T", bound="TaskShort")



@_attrs_define
class TaskShort:
    """ 
        Attributes:
            id (str):  Example: zdc3Pyhyz3m8vjDeM.
            user_id (str):  Example: wRsJZtadYvn4mBZmm.
            act_id (str):  Example: asADASadYvn4mBZmm.
            act_name (str):  Example: my-actor.
            name (str):  Example: my-task.
            act_username (str):  Example: janedoe.
            created_at (str):  Example: 2018-10-26T07:23:14.855Z.
            modified_at (str):  Example: 2018-10-26T13:30:49.578Z.
            username (None | str | Unset):  Example: janedoe.
            stats (TaskShortStats | Unset):
     """

    id: str
    user_id: str
    act_id: str
    act_name: str
    name: str
    act_username: str
    created_at: str
    modified_at: str
    username: None | str | Unset = UNSET
    stats: TaskShortStats | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.task_short_stats import TaskShortStats
        id = self.id

        user_id = self.user_id

        act_id = self.act_id

        act_name = self.act_name

        name = self.name

        act_username = self.act_username

        created_at = self.created_at

        modified_at = self.modified_at

        username: None | str | Unset
        if isinstance(self.username, Unset):
            username = UNSET
        else:
            username = self.username

        stats: dict[str, Any] | Unset = UNSET
        if not isinstance(self.stats, Unset):
            stats = self.stats.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "userId": user_id,
            "actId": act_id,
            "actName": act_name,
            "name": name,
            "actUsername": act_username,
            "createdAt": created_at,
            "modifiedAt": modified_at,
        })
        if username is not UNSET:
            field_dict["username"] = username
        if stats is not UNSET:
            field_dict["stats"] = stats

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.task_short_stats import TaskShortStats
        d = dict(src_dict)
        id = d.pop("id")

        user_id = d.pop("userId")

        act_id = d.pop("actId")

        act_name = d.pop("actName")

        name = d.pop("name")

        act_username = d.pop("actUsername")

        created_at = d.pop("createdAt")

        modified_at = d.pop("modifiedAt")

        def _parse_username(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        username = _parse_username(d.pop("username", UNSET))


        _stats = d.pop("stats", UNSET)
        stats: TaskShortStats | Unset
        if isinstance(_stats,  Unset):
            stats = UNSET
        else:
            stats = TaskShortStats.from_dict(_stats)




        task_short = cls(
            id=id,
            user_id=user_id,
            act_id=act_id,
            act_name=act_name,
            name=name,
            act_username=act_username,
            created_at=created_at,
            modified_at=modified_at,
            username=username,
            stats=stats,
        )


        task_short.additional_properties = d
        return task_short

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
