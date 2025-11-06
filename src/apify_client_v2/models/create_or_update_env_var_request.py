from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast






T = TypeVar("T", bound="CreateOrUpdateEnvVarRequest")



@_attrs_define
class CreateOrUpdateEnvVarRequest:
    """ 
        Attributes:
            name (str):  Example: MY_ENV_VAR.
            value (str):  Example: my-new-value.
            is_secret (bool | None | Unset):
     """

    name: str
    value: str
    is_secret: bool | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        name = self.name

        value = self.value

        is_secret: bool | None | Unset
        if isinstance(self.is_secret, Unset):
            is_secret = UNSET
        else:
            is_secret = self.is_secret


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "name": name,
            "value": value,
        })
        if is_secret is not UNSET:
            field_dict["isSecret"] = is_secret

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        value = d.pop("value")

        def _parse_is_secret(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        is_secret = _parse_is_secret(d.pop("isSecret", UNSET))


        create_or_update_env_var_request = cls(
            name=name,
            value=value,
            is_secret=is_secret,
        )


        create_or_update_env_var_request.additional_properties = d
        return create_or_update_env_var_request

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
