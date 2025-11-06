from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.dataset_stats import DatasetStats
  from ..models.dataset_schema_type_0 import DatasetSchemaType0





T = TypeVar("T", bound="Dataset")



@_attrs_define
class Dataset:
    """ 
        Attributes:
            id (str):  Example: WkzbQMuFYuamGv3YF.
            name (str):  Example: d7b9MDYsbtX5L7XAj.
            user_id (str):  Example: wRsJZtadYvn4mBZmm.
            created_at (str):  Example: 2019-12-12T07:34:14.202Z.
            modified_at (str):  Example: 2019-12-13T08:36:13.202Z.
            accessed_at (str):  Example: 2019-12-14T08:36:13.202Z.
            item_count (float):  Example: 7.
            clean_item_count (float):  Example: 5.
            console_url (str):  Example: https://console.apify.com/storage/datasets/27TmTznX9YPeAYhkC.
            act_id (None | str | Unset):
            act_run_id (None | str | Unset):
            fields (list[str] | None | Unset):
            schema (DatasetSchemaType0 | None | Unset): Defines the schema of items in your dataset, the full specification
                can be found in [Apify docs](/platform/actors/development/actor-definition/dataset-schema) Example:
                {'actorSpecification': 1, 'title': 'My dataset', 'views': {'overview': {'title': 'Overview', 'transformation':
                {'fields': ['linkUrl']}, 'display': {'component': 'table', 'properties': {'linkUrl': {'label': 'Link URL',
                'format': 'link'}}}}}}.
            items_public_url (str | Unset): A public link to access the dataset items directly. Example:
                https://api.apify.com/v2/datasets/WkzbQMuFYuamGv3YF/items?signature=abc123.
            url_signing_secret_key (None | str | Unset): A secret key for generating signed public URLs. It is only provided
                to clients with WRITE permission for the dataset.
            stats (DatasetStats | Unset):
     """

    id: str
    name: str
    user_id: str
    created_at: str
    modified_at: str
    accessed_at: str
    item_count: float
    clean_item_count: float
    console_url: str
    act_id: None | str | Unset = UNSET
    act_run_id: None | str | Unset = UNSET
    fields: list[str] | None | Unset = UNSET
    schema: DatasetSchemaType0 | None | Unset = UNSET
    items_public_url: str | Unset = UNSET
    url_signing_secret_key: None | str | Unset = UNSET
    stats: DatasetStats | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.dataset_stats import DatasetStats
        from ..models.dataset_schema_type_0 import DatasetSchemaType0
        id = self.id

        name = self.name

        user_id = self.user_id

        created_at = self.created_at

        modified_at = self.modified_at

        accessed_at = self.accessed_at

        item_count = self.item_count

        clean_item_count = self.clean_item_count

        console_url = self.console_url

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

        fields: list[str] | None | Unset
        if isinstance(self.fields, Unset):
            fields = UNSET
        elif isinstance(self.fields, list):
            fields = self.fields


        else:
            fields = self.fields

        schema: dict[str, Any] | None | Unset
        if isinstance(self.schema, Unset):
            schema = UNSET
        elif isinstance(self.schema, DatasetSchemaType0):
            schema = self.schema.to_dict()
        else:
            schema = self.schema

        items_public_url = self.items_public_url

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
            "userId": user_id,
            "createdAt": created_at,
            "modifiedAt": modified_at,
            "accessedAt": accessed_at,
            "itemCount": item_count,
            "cleanItemCount": clean_item_count,
            "consoleUrl": console_url,
        })
        if act_id is not UNSET:
            field_dict["actId"] = act_id
        if act_run_id is not UNSET:
            field_dict["actRunId"] = act_run_id
        if fields is not UNSET:
            field_dict["fields"] = fields
        if schema is not UNSET:
            field_dict["schema"] = schema
        if items_public_url is not UNSET:
            field_dict["itemsPublicUrl"] = items_public_url
        if url_signing_secret_key is not UNSET:
            field_dict["urlSigningSecretKey"] = url_signing_secret_key
        if stats is not UNSET:
            field_dict["stats"] = stats

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.dataset_stats import DatasetStats
        from ..models.dataset_schema_type_0 import DatasetSchemaType0
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        user_id = d.pop("userId")

        created_at = d.pop("createdAt")

        modified_at = d.pop("modifiedAt")

        accessed_at = d.pop("accessedAt")

        item_count = d.pop("itemCount")

        clean_item_count = d.pop("cleanItemCount")

        console_url = d.pop("consoleUrl")

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


        def _parse_fields(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                fields_type_0 = cast(list[str], data)

                return fields_type_0
            except: # noqa: E722
                pass
            return cast(list[str] | None | Unset, data)

        fields = _parse_fields(d.pop("fields", UNSET))


        def _parse_schema(data: object) -> DatasetSchemaType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                schema_type_0 = DatasetSchemaType0.from_dict(data)



                return schema_type_0
            except: # noqa: E722
                pass
            return cast(DatasetSchemaType0 | None | Unset, data)

        schema = _parse_schema(d.pop("schema", UNSET))


        items_public_url = d.pop("itemsPublicUrl", UNSET)

        def _parse_url_signing_secret_key(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        url_signing_secret_key = _parse_url_signing_secret_key(d.pop("urlSigningSecretKey", UNSET))


        _stats = d.pop("stats", UNSET)
        stats: DatasetStats | Unset
        if isinstance(_stats,  Unset):
            stats = UNSET
        else:
            stats = DatasetStats.from_dict(_stats)




        dataset = cls(
            id=id,
            name=name,
            user_id=user_id,
            created_at=created_at,
            modified_at=modified_at,
            accessed_at=accessed_at,
            item_count=item_count,
            clean_item_count=clean_item_count,
            console_url=console_url,
            act_id=act_id,
            act_run_id=act_run_id,
            fields=fields,
            schema=schema,
            items_public_url=items_public_url,
            url_signing_secret_key=url_signing_secret_key,
            stats=stats,
        )


        dataset.additional_properties = d
        return dataset

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
