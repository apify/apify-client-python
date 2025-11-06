from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
  from ..models.limits import Limits
  from ..models.monthly_usage_cycle import MonthlyUsageCycle
  from ..models.current import Current





T = TypeVar("T", bound="AccountLimits")



@_attrs_define
class AccountLimits:
    """ 
        Attributes:
            monthly_usage_cycle (MonthlyUsageCycle):
            limits (Limits):
            current (Current):
     """

    monthly_usage_cycle: MonthlyUsageCycle
    limits: Limits
    current: Current
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.limits import Limits
        from ..models.monthly_usage_cycle import MonthlyUsageCycle
        from ..models.current import Current
        monthly_usage_cycle = self.monthly_usage_cycle.to_dict()

        limits = self.limits.to_dict()

        current = self.current.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "monthlyUsageCycle": monthly_usage_cycle,
            "limits": limits,
            "current": current,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.limits import Limits
        from ..models.monthly_usage_cycle import MonthlyUsageCycle
        from ..models.current import Current
        d = dict(src_dict)
        monthly_usage_cycle = MonthlyUsageCycle.from_dict(d.pop("monthlyUsageCycle"))




        limits = Limits.from_dict(d.pop("limits"))




        current = Current.from_dict(d.pop("current"))




        account_limits = cls(
            monthly_usage_cycle=monthly_usage_cycle,
            limits=limits,
            current=current,
        )


        account_limits.additional_properties = d
        return account_limits

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
