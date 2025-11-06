from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.get_open_api_response_servers_item import GetOpenApiResponseServersItem
  from ..models.get_open_api_response_components import GetOpenApiResponseComponents
  from ..models.get_open_api_response_info import GetOpenApiResponseInfo
  from ..models.get_open_api_response_paths import GetOpenApiResponsePaths





T = TypeVar("T", bound="GetOpenApiResponse")



@_attrs_define
class GetOpenApiResponse:
    """ 
        Attributes:
            openapi (str | Unset):  Example: 3.0.1.
            info (GetOpenApiResponseInfo | Unset):
            servers (list[GetOpenApiResponseServersItem] | Unset):
            paths (GetOpenApiResponsePaths | Unset):
            components (GetOpenApiResponseComponents | Unset):
     """

    openapi: str | Unset = UNSET
    info: GetOpenApiResponseInfo | Unset = UNSET
    servers: list[GetOpenApiResponseServersItem] | Unset = UNSET
    paths: GetOpenApiResponsePaths | Unset = UNSET
    components: GetOpenApiResponseComponents | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.get_open_api_response_servers_item import GetOpenApiResponseServersItem
        from ..models.get_open_api_response_components import GetOpenApiResponseComponents
        from ..models.get_open_api_response_info import GetOpenApiResponseInfo
        from ..models.get_open_api_response_paths import GetOpenApiResponsePaths
        openapi = self.openapi

        info: dict[str, Any] | Unset = UNSET
        if not isinstance(self.info, Unset):
            info = self.info.to_dict()

        servers: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.servers, Unset):
            servers = []
            for servers_item_data in self.servers:
                servers_item = servers_item_data.to_dict()
                servers.append(servers_item)



        paths: dict[str, Any] | Unset = UNSET
        if not isinstance(self.paths, Unset):
            paths = self.paths.to_dict()

        components: dict[str, Any] | Unset = UNSET
        if not isinstance(self.components, Unset):
            components = self.components.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if openapi is not UNSET:
            field_dict["openapi"] = openapi
        if info is not UNSET:
            field_dict["info"] = info
        if servers is not UNSET:
            field_dict["servers"] = servers
        if paths is not UNSET:
            field_dict["paths"] = paths
        if components is not UNSET:
            field_dict["components"] = components

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_open_api_response_servers_item import GetOpenApiResponseServersItem
        from ..models.get_open_api_response_components import GetOpenApiResponseComponents
        from ..models.get_open_api_response_info import GetOpenApiResponseInfo
        from ..models.get_open_api_response_paths import GetOpenApiResponsePaths
        d = dict(src_dict)
        openapi = d.pop("openapi", UNSET)

        _info = d.pop("info", UNSET)
        info: GetOpenApiResponseInfo | Unset
        if isinstance(_info,  Unset):
            info = UNSET
        else:
            info = GetOpenApiResponseInfo.from_dict(_info)




        servers = []
        _servers = d.pop("servers", UNSET)
        for servers_item_data in (_servers or []):
            servers_item = GetOpenApiResponseServersItem.from_dict(servers_item_data)



            servers.append(servers_item)


        _paths = d.pop("paths", UNSET)
        paths: GetOpenApiResponsePaths | Unset
        if isinstance(_paths,  Unset):
            paths = UNSET
        else:
            paths = GetOpenApiResponsePaths.from_dict(_paths)




        _components = d.pop("components", UNSET)
        components: GetOpenApiResponseComponents | Unset
        if isinstance(_components,  Unset):
            components = UNSET
        else:
            components = GetOpenApiResponseComponents.from_dict(_components)




        get_open_api_response = cls(
            openapi=openapi,
            info=info,
            servers=servers,
            paths=paths,
            components=components,
        )


        get_open_api_response.additional_properties = d
        return get_open_api_response

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
