from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.tagged_builds_latest_type_1 import TaggedBuildsLatestType1





T = TypeVar("T", bound="TaggedBuilds")



@_attrs_define
class TaggedBuilds:
    """ 
        Attributes:
            latest (Any | TaggedBuildsLatestType1 | Unset):
     """

    latest: Any | TaggedBuildsLatestType1 | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.tagged_builds_latest_type_1 import TaggedBuildsLatestType1
        latest: Any | dict[str, Any] | Unset
        if isinstance(self.latest, Unset):
            latest = UNSET
        elif isinstance(self.latest, TaggedBuildsLatestType1):
            latest = self.latest.to_dict()
        else:
            latest = self.latest


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if latest is not UNSET:
            field_dict["latest"] = latest

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.tagged_builds_latest_type_1 import TaggedBuildsLatestType1
        d = dict(src_dict)
        def _parse_latest(data: object) -> Any | TaggedBuildsLatestType1 | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                latest_type_1 = TaggedBuildsLatestType1.from_dict(data)



                return latest_type_1
            except: # noqa: E722
                pass
            return cast(Any | TaggedBuildsLatestType1 | Unset, data)

        latest = _parse_latest(d.pop("latest", UNSET))


        tagged_builds = cls(
            latest=latest,
        )


        tagged_builds.additional_properties = d
        return tagged_builds

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
