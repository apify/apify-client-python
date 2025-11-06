from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.update_task_request_options import UpdateTaskRequestOptions
  from ..models.update_task_request_input import UpdateTaskRequestInput
  from ..models.update_task_request_stats import UpdateTaskRequestStats





T = TypeVar("T", bound="UpdateTaskRequest")



@_attrs_define
class UpdateTaskRequest:
    """ 
        Attributes:
            id (str):  Example: ZxLNxrRaZrSjuhT9y.
            user_id (str):  Example: BPWZBd7Z9c746JAnF.
            act_id (str):  Example: asADASadYvn4mBZmm.
            name (str):  Example: my-task.
            created_at (str):  Example: 2018-10-26T07:23:14.855Z.
            modified_at (str):  Example: 2018-10-26T13:30:49.578Z.
            username (None | str | Unset):  Example: janedoe.
            removed_at (None | str | Unset):
            stats (UpdateTaskRequestStats | Unset):
            options (UpdateTaskRequestOptions | Unset):
            input_ (UpdateTaskRequestInput | Unset):
     """

    id: str
    user_id: str
    act_id: str
    name: str
    created_at: str
    modified_at: str
    username: None | str | Unset = UNSET
    removed_at: None | str | Unset = UNSET
    stats: UpdateTaskRequestStats | Unset = UNSET
    options: UpdateTaskRequestOptions | Unset = UNSET
    input_: UpdateTaskRequestInput | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.update_task_request_options import UpdateTaskRequestOptions
        from ..models.update_task_request_input import UpdateTaskRequestInput
        from ..models.update_task_request_stats import UpdateTaskRequestStats
        id = self.id

        user_id = self.user_id

        act_id = self.act_id

        name = self.name

        created_at = self.created_at

        modified_at = self.modified_at

        username: None | str | Unset
        if isinstance(self.username, Unset):
            username = UNSET
        else:
            username = self.username

        removed_at: None | str | Unset
        if isinstance(self.removed_at, Unset):
            removed_at = UNSET
        else:
            removed_at = self.removed_at

        stats: dict[str, Any] | Unset = UNSET
        if not isinstance(self.stats, Unset):
            stats = self.stats.to_dict()

        options: dict[str, Any] | Unset = UNSET
        if not isinstance(self.options, Unset):
            options = self.options.to_dict()

        input_: dict[str, Any] | Unset = UNSET
        if not isinstance(self.input_, Unset):
            input_ = self.input_.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "userId": user_id,
            "actId": act_id,
            "name": name,
            "createdAt": created_at,
            "modifiedAt": modified_at,
        })
        if username is not UNSET:
            field_dict["username"] = username
        if removed_at is not UNSET:
            field_dict["removedAt"] = removed_at
        if stats is not UNSET:
            field_dict["stats"] = stats
        if options is not UNSET:
            field_dict["options"] = options
        if input_ is not UNSET:
            field_dict["input"] = input_

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.update_task_request_options import UpdateTaskRequestOptions
        from ..models.update_task_request_input import UpdateTaskRequestInput
        from ..models.update_task_request_stats import UpdateTaskRequestStats
        d = dict(src_dict)
        id = d.pop("id")

        user_id = d.pop("userId")

        act_id = d.pop("actId")

        name = d.pop("name")

        created_at = d.pop("createdAt")

        modified_at = d.pop("modifiedAt")

        def _parse_username(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        username = _parse_username(d.pop("username", UNSET))


        def _parse_removed_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        removed_at = _parse_removed_at(d.pop("removedAt", UNSET))


        _stats = d.pop("stats", UNSET)
        stats: UpdateTaskRequestStats | Unset
        if isinstance(_stats,  Unset):
            stats = UNSET
        else:
            stats = UpdateTaskRequestStats.from_dict(_stats)




        _options = d.pop("options", UNSET)
        options: UpdateTaskRequestOptions | Unset
        if isinstance(_options,  Unset):
            options = UNSET
        else:
            options = UpdateTaskRequestOptions.from_dict(_options)




        _input_ = d.pop("input", UNSET)
        input_: UpdateTaskRequestInput | Unset
        if isinstance(_input_,  Unset):
            input_ = UNSET
        else:
            input_ = UpdateTaskRequestInput.from_dict(_input_)




        update_task_request = cls(
            id=id,
            user_id=user_id,
            act_id=act_id,
            name=name,
            created_at=created_at,
            modified_at=modified_at,
            username=username,
            removed_at=removed_at,
            stats=stats,
            options=options,
            input_=input_,
        )


        update_task_request.additional_properties = d
        return update_task_request

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
