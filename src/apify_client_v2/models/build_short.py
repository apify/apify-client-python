from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.build_short_meta import BuildShortMeta





T = TypeVar("T", bound="BuildShort")



@_attrs_define
class BuildShort:
    """ 
        Attributes:
            id (str):  Example: HG7ML7M8z78YcAPEB.
            status (str):  Example: SUCCEEDED.
            started_at (str):  Example: 2019-11-30T07:34:24.202Z.
            finished_at (str):  Example: 2019-12-12T09:30:12.202Z.
            usage_total_usd (float):  Example: 0.02.
            act_id (str | Unset):  Example: janedoe~my-actor.
            meta (BuildShortMeta | Unset):
     """

    id: str
    status: str
    started_at: str
    finished_at: str
    usage_total_usd: float
    act_id: str | Unset = UNSET
    meta: BuildShortMeta | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.build_short_meta import BuildShortMeta
        id = self.id

        status = self.status

        started_at = self.started_at

        finished_at = self.finished_at

        usage_total_usd = self.usage_total_usd

        act_id = self.act_id

        meta: dict[str, Any] | Unset = UNSET
        if not isinstance(self.meta, Unset):
            meta = self.meta.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "status": status,
            "startedAt": started_at,
            "finishedAt": finished_at,
            "usageTotalUsd": usage_total_usd,
        })
        if act_id is not UNSET:
            field_dict["actId"] = act_id
        if meta is not UNSET:
            field_dict["meta"] = meta

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.build_short_meta import BuildShortMeta
        d = dict(src_dict)
        id = d.pop("id")

        status = d.pop("status")

        started_at = d.pop("startedAt")

        finished_at = d.pop("finishedAt")

        usage_total_usd = d.pop("usageTotalUsd")

        act_id = d.pop("actId", UNSET)

        _meta = d.pop("meta", UNSET)
        meta: BuildShortMeta | Unset
        if isinstance(_meta,  Unset):
            meta = UNSET
        else:
            meta = BuildShortMeta.from_dict(_meta)




        build_short = cls(
            id=id,
            status=status,
            started_at=started_at,
            finished_at=finished_at,
            usage_total_usd=usage_total_usd,
            act_id=act_id,
            meta=meta,
        )


        build_short.additional_properties = d
        return build_short

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
