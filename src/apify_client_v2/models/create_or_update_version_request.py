from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.version_source_type import VersionSourceType
from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.env_var import EnvVar
  from ..models.source_code_folder import SourceCodeFolder
  from ..models.source_code_file import SourceCodeFile





T = TypeVar("T", bound="CreateOrUpdateVersionRequest")



@_attrs_define
class CreateOrUpdateVersionRequest:
    """ 
        Attributes:
            version_number (None | str | Unset):  Example: 0.0.
            source_type (Any | Unset | VersionSourceType):
            env_vars (list[EnvVar] | None | Unset):
            apply_env_vars_to_build (bool | None | Unset):
            build_tag (None | str | Unset):  Example: latest.
            source_files (list[SourceCodeFile | SourceCodeFolder] | Unset):
     """

    version_number: None | str | Unset = UNSET
    source_type: Any | Unset | VersionSourceType = UNSET
    env_vars: list[EnvVar] | None | Unset = UNSET
    apply_env_vars_to_build: bool | None | Unset = UNSET
    build_tag: None | str | Unset = UNSET
    source_files: list[SourceCodeFile | SourceCodeFolder] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.env_var import EnvVar
        from ..models.source_code_folder import SourceCodeFolder
        from ..models.source_code_file import SourceCodeFile
        version_number: None | str | Unset
        if isinstance(self.version_number, Unset):
            version_number = UNSET
        else:
            version_number = self.version_number

        source_type: Any | str | Unset
        if isinstance(self.source_type, Unset):
            source_type = UNSET
        elif isinstance(self.source_type, VersionSourceType):
            source_type = self.source_type.value
        else:
            source_type = self.source_type

        env_vars: list[dict[str, Any]] | None | Unset
        if isinstance(self.env_vars, Unset):
            env_vars = UNSET
        elif isinstance(self.env_vars, list):
            env_vars = []
            for env_vars_type_0_item_data in self.env_vars:
                env_vars_type_0_item = env_vars_type_0_item_data.to_dict()
                env_vars.append(env_vars_type_0_item)


        else:
            env_vars = self.env_vars

        apply_env_vars_to_build: bool | None | Unset
        if isinstance(self.apply_env_vars_to_build, Unset):
            apply_env_vars_to_build = UNSET
        else:
            apply_env_vars_to_build = self.apply_env_vars_to_build

        build_tag: None | str | Unset
        if isinstance(self.build_tag, Unset):
            build_tag = UNSET
        else:
            build_tag = self.build_tag

        source_files: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.source_files, Unset):
            source_files = []
            for componentsschemas_version_source_files_item_data in self.source_files:
                componentsschemas_version_source_files_item: dict[str, Any]
                if isinstance(componentsschemas_version_source_files_item_data, SourceCodeFile):
                    componentsschemas_version_source_files_item = componentsschemas_version_source_files_item_data.to_dict()
                else:
                    componentsschemas_version_source_files_item = componentsschemas_version_source_files_item_data.to_dict()

                source_files.append(componentsschemas_version_source_files_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if version_number is not UNSET:
            field_dict["versionNumber"] = version_number
        if source_type is not UNSET:
            field_dict["sourceType"] = source_type
        if env_vars is not UNSET:
            field_dict["envVars"] = env_vars
        if apply_env_vars_to_build is not UNSET:
            field_dict["applyEnvVarsToBuild"] = apply_env_vars_to_build
        if build_tag is not UNSET:
            field_dict["buildTag"] = build_tag
        if source_files is not UNSET:
            field_dict["sourceFiles"] = source_files

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.env_var import EnvVar
        from ..models.source_code_folder import SourceCodeFolder
        from ..models.source_code_file import SourceCodeFile
        d = dict(src_dict)
        def _parse_version_number(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        version_number = _parse_version_number(d.pop("versionNumber", UNSET))


        def _parse_source_type(data: object) -> Any | Unset | VersionSourceType:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                source_type_type_1 = VersionSourceType(data)



                return source_type_type_1
            except: # noqa: E722
                pass
            return cast(Any | Unset | VersionSourceType, data)

        source_type = _parse_source_type(d.pop("sourceType", UNSET))


        def _parse_env_vars(data: object) -> list[EnvVar] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                env_vars_type_0 = []
                _env_vars_type_0 = data
                for env_vars_type_0_item_data in (_env_vars_type_0):
                    env_vars_type_0_item = EnvVar.from_dict(env_vars_type_0_item_data)



                    env_vars_type_0.append(env_vars_type_0_item)

                return env_vars_type_0
            except: # noqa: E722
                pass
            return cast(list[EnvVar] | None | Unset, data)

        env_vars = _parse_env_vars(d.pop("envVars", UNSET))


        def _parse_apply_env_vars_to_build(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        apply_env_vars_to_build = _parse_apply_env_vars_to_build(d.pop("applyEnvVarsToBuild", UNSET))


        def _parse_build_tag(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        build_tag = _parse_build_tag(d.pop("buildTag", UNSET))


        source_files = []
        _source_files = d.pop("sourceFiles", UNSET)
        for componentsschemas_version_source_files_item_data in (_source_files or []):
            def _parse_componentsschemas_version_source_files_item(data: object) -> SourceCodeFile | SourceCodeFolder:
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemas_version_source_files_item_source_code_file = SourceCodeFile.from_dict(data)



                    return componentsschemas_version_source_files_item_source_code_file
                except: # noqa: E722
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_version_source_files_item_source_code_folder = SourceCodeFolder.from_dict(data)



                return componentsschemas_version_source_files_item_source_code_folder

            componentsschemas_version_source_files_item = _parse_componentsschemas_version_source_files_item(componentsschemas_version_source_files_item_data)

            source_files.append(componentsschemas_version_source_files_item)


        create_or_update_version_request = cls(
            version_number=version_number,
            source_type=source_type,
            env_vars=env_vars,
            apply_env_vars_to_build=apply_env_vars_to_build,
            build_tag=build_tag,
            source_files=source_files,
        )


        create_or_update_version_request.additional_properties = d
        return create_or_update_version_request

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
