from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.create_task_request_options import CreateTaskRequestOptions
  from ..models.create_task_request_input import CreateTaskRequestInput





T = TypeVar("T", bound="ActorTasksPostBody")



@_attrs_define
class ActorTasksPostBody:
    """ 
        Attributes:
            act_id (str):  Example: asADASadYvn4mBZmm.
            name (str):  Example: my-task.
            options (CreateTaskRequestOptions | Unset):
            input_ (CreateTaskRequestInput | Unset):
     """

    act_id: str
    name: str
    options: CreateTaskRequestOptions | Unset = UNSET
    input_: CreateTaskRequestInput | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.create_task_request_options import CreateTaskRequestOptions
        from ..models.create_task_request_input import CreateTaskRequestInput
        act_id = self.act_id

        name = self.name

        options: dict[str, Any] | Unset = UNSET
        if not isinstance(self.options, Unset):
            options = self.options.to_dict()

        input_: dict[str, Any] | Unset = UNSET
        if not isinstance(self.input_, Unset):
            input_ = self.input_.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "actId": act_id,
            "name": name,
        })
        if options is not UNSET:
            field_dict["options"] = options
        if input_ is not UNSET:
            field_dict["input"] = input_

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.create_task_request_options import CreateTaskRequestOptions
        from ..models.create_task_request_input import CreateTaskRequestInput
        d = dict(src_dict)
        act_id = d.pop("actId")

        name = d.pop("name")

        _options = d.pop("options", UNSET)
        options: CreateTaskRequestOptions | Unset
        if isinstance(_options,  Unset):
            options = UNSET
        else:
            options = CreateTaskRequestOptions.from_dict(_options)




        _input_ = d.pop("input", UNSET)
        input_: CreateTaskRequestInput | Unset
        if isinstance(_input_,  Unset):
            input_ = UNSET
        else:
            input_ = CreateTaskRequestInput.from_dict(_input_)




        actor_tasks_post_body = cls(
            act_id=act_id,
            name=name,
            options=options,
            input_=input_,
        )


        actor_tasks_post_body.additional_properties = d
        return actor_tasks_post_body

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
