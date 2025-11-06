from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
  from ..models.act_update_tagged_builds_type_0_additional_property_type_0 import ActUpdateTaggedBuildsType0AdditionalPropertyType0





T = TypeVar("T", bound="ActUpdateTaggedBuildsType0")



@_attrs_define
class ActUpdateTaggedBuildsType0:
    """ An object to modify tags on the Actor's builds. The key is the tag name (e.g., _latest_), and the value is either an
    object with a `buildId` or `null`.

    This operation is a patch; any existing tags that you omit from this object will be preserved.

    - **To create or reassign a tag**, provide the tag name with a `buildId`. e.g., to assign the _latest_ tag:

      &nbsp;

      ```json
      {
        "latest": {
          "buildId": "z2EryhbfhgSyqj6Hn"
        }
      }
      ```

    - **To remove a tag**, provide the tag name with a `null` value. e.g., to remove the _beta_ tag:

      &nbsp;

      ```json
      {
        "beta": null
      }
      ```

    - **To perform multiple operations**, combine them. The following reassigns _latest_ and removes _beta_, while
    preserving any other existing tags.

      &nbsp;

      ```json
      {
        "latest": {
          "buildId": "z2EryhbfhgSyqj6Hn"
        },
        "beta": null
      }
      ```

        Example:
            {'latest': {'buildId': 'z2EryhbfhgSyqj6Hn'}, 'beta': None}

     """

    additional_properties: dict[str, ActUpdateTaggedBuildsType0AdditionalPropertyType0 | None] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.act_update_tagged_builds_type_0_additional_property_type_0 import ActUpdateTaggedBuildsType0AdditionalPropertyType0
        
        field_dict: dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            
            if isinstance(prop, ActUpdateTaggedBuildsType0AdditionalPropertyType0):
                field_dict[prop_name] = prop.to_dict()
            else:
                field_dict[prop_name] = prop


        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.act_update_tagged_builds_type_0_additional_property_type_0 import ActUpdateTaggedBuildsType0AdditionalPropertyType0
        d = dict(src_dict)
        act_update_tagged_builds_type_0 = cls(
        )


        additional_properties = {}
        for prop_name, prop_dict in d.items():
            def _parse_additional_property(data: object) -> ActUpdateTaggedBuildsType0AdditionalPropertyType0 | None:
                if data is None:
                    return data
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    additional_property_type_0 = ActUpdateTaggedBuildsType0AdditionalPropertyType0.from_dict(data)



                    return additional_property_type_0
                except: # noqa: E722
                    pass
                return cast(ActUpdateTaggedBuildsType0AdditionalPropertyType0 | None, data)

            additional_property = _parse_additional_property(prop_dict)

            additional_properties[prop_name] = additional_property

        act_update_tagged_builds_type_0.additional_properties = additional_properties
        return act_update_tagged_builds_type_0

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> ActUpdateTaggedBuildsType0AdditionalPropertyType0 | None:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: ActUpdateTaggedBuildsType0AdditionalPropertyType0 | None) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
