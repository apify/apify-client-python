from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.key_value_store_stats import KeyValueStoreStats





T = TypeVar("T", bound="KeyValueStore")



@_attrs_define
class KeyValueStore:
    """ 
        Attributes:
            id (str):  Example: WkzbQMuFYuamGv3YF.
            name (str):  Example: d7b9MDYsbtX5L7XAj.
            created_at (str):  Example: 2019-12-12T07:34:14.202Z.
            modified_at (str):  Example: 2019-12-13T08:36:13.202Z.
            accessed_at (str):  Example: 2019-12-14T08:36:13.202Z.
            console_url (str):  Example: https://console.apify.com/storage/key-value-stores/27TmTznX9YPeAYhkC.
            keys_public_url (str): A public link to access keys of the key-value store directly. Example:
                https://api.apify.com/v2/key-value-stores/WkzbQMuFYuamGv3YF/keys?signature=abc123.
            user_id (None | str | Unset):  Example: BPWDBd7Z9c746JAnF.
            username (None | str | Unset):  Example: janedoe.
            act_id (None | str | Unset):
            act_run_id (None | str | Unset):
            url_signing_secret_key (None | str | Unset): A secret key for generating signed public URLs. It is only provided
                to clients with WRITE permission for the key-value store.
            stats (KeyValueStoreStats | Unset):
     """

    id: str
    name: str
    created_at: str
    modified_at: str
    accessed_at: str
    console_url: str
    keys_public_url: str
    user_id: None | str | Unset = UNSET
    username: None | str | Unset = UNSET
    act_id: None | str | Unset = UNSET
    act_run_id: None | str | Unset = UNSET
    url_signing_secret_key: None | str | Unset = UNSET
    stats: KeyValueStoreStats | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.key_value_store_stats import KeyValueStoreStats
        id = self.id

        name = self.name

        created_at = self.created_at

        modified_at = self.modified_at

        accessed_at = self.accessed_at

        console_url = self.console_url

        keys_public_url = self.keys_public_url

        user_id: None | str | Unset
        if isinstance(self.user_id, Unset):
            user_id = UNSET
        else:
            user_id = self.user_id

        username: None | str | Unset
        if isinstance(self.username, Unset):
            username = UNSET
        else:
            username = self.username

        act_id: None | str | Unset
        if isinstance(self.act_id, Unset):
            act_id = UNSET
        else:
            act_id = self.act_id

        act_run_id: None | str | Unset
        if isinstance(self.act_run_id, Unset):
            act_run_id = UNSET
        else:
            act_run_id = self.act_run_id

        url_signing_secret_key: None | str | Unset
        if isinstance(self.url_signing_secret_key, Unset):
            url_signing_secret_key = UNSET
        else:
            url_signing_secret_key = self.url_signing_secret_key

        stats: dict[str, Any] | Unset = UNSET
        if not isinstance(self.stats, Unset):
            stats = self.stats.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "name": name,
            "createdAt": created_at,
            "modifiedAt": modified_at,
            "accessedAt": accessed_at,
            "consoleUrl": console_url,
            "keysPublicUrl": keys_public_url,
        })
        if user_id is not UNSET:
            field_dict["userId"] = user_id
        if username is not UNSET:
            field_dict["username"] = username
        if act_id is not UNSET:
            field_dict["actId"] = act_id
        if act_run_id is not UNSET:
            field_dict["actRunId"] = act_run_id
        if url_signing_secret_key is not UNSET:
            field_dict["urlSigningSecretKey"] = url_signing_secret_key
        if stats is not UNSET:
            field_dict["stats"] = stats

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.key_value_store_stats import KeyValueStoreStats
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        created_at = d.pop("createdAt")

        modified_at = d.pop("modifiedAt")

        accessed_at = d.pop("accessedAt")

        console_url = d.pop("consoleUrl")

        keys_public_url = d.pop("keysPublicUrl")

        def _parse_user_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        user_id = _parse_user_id(d.pop("userId", UNSET))


        def _parse_username(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        username = _parse_username(d.pop("username", UNSET))


        def _parse_act_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        act_id = _parse_act_id(d.pop("actId", UNSET))


        def _parse_act_run_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        act_run_id = _parse_act_run_id(d.pop("actRunId", UNSET))


        def _parse_url_signing_secret_key(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        url_signing_secret_key = _parse_url_signing_secret_key(d.pop("urlSigningSecretKey", UNSET))


        _stats = d.pop("stats", UNSET)
        stats: KeyValueStoreStats | Unset
        if isinstance(_stats,  Unset):
            stats = UNSET
        else:
            stats = KeyValueStoreStats.from_dict(_stats)




        key_value_store = cls(
            id=id,
            name=name,
            created_at=created_at,
            modified_at=modified_at,
            accessed_at=accessed_at,
            console_url=console_url,
            keys_public_url=keys_public_url,
            user_id=user_id,
            username=username,
            act_id=act_id,
            act_run_id=act_run_id,
            url_signing_secret_key=url_signing_secret_key,
            stats=stats,
        )


        key_value_store.additional_properties = d
        return key_value_store

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
