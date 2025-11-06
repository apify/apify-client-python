from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.actor_definition_actor_specification import ActorDefinitionActorSpecification
from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.actor_definition_storages import ActorDefinitionStorages
  from ..models.actor_definition_input import ActorDefinitionInput
  from ..models.actor_definition_environment_variables import ActorDefinitionEnvironmentVariables





T = TypeVar("T", bound="ActorDefinition")



@_attrs_define
class ActorDefinition:
    """ The definition of the Actor, the full specification of this field can be found in [Apify
    docs](https://docs.apify.com/platform/actors/development/actor-definition/actor-json)

        Attributes:
            actor_specification (ActorDefinitionActorSpecification): The Actor specification version that this Actor
                follows. This property must be set to 1.
            name (str): The name of the Actor.
            version (str): The version of the Actor, specified in the format [Number].[Number], e.g., 0.1, 1.0.
            build_tag (str | Unset): The tag name to be applied to a successful build of the Actor. Defaults to 'latest' if
                not specified.
            environment_variables (ActorDefinitionEnvironmentVariables | Unset): A map of environment variables to be used
                during local development and deployment.
            dockerfile (str | Unset): The path to the Dockerfile used for building the Actor on the platform.
            docker_context_dir (str | Unset): The path to the directory used as the Docker context when building the Actor.
            readme (str | Unset): The path to the README file for the Actor.
            input_ (ActorDefinitionInput | Unset): The input schema object, the full specification can be found in [Apify
                docs](https://docs.apify.com/platform/actors/development/actor-definition/input-schema)
            changelog (str | Unset): The path to the CHANGELOG file displayed in the Actor's information tab.
            storages (ActorDefinitionStorages | Unset):
            min_memory_mbytes (int | Unset): Specifies the minimum amount of memory in megabytes required by the Actor.
            max_memory_mbytes (int | Unset): Specifies the maximum amount of memory in megabytes required by the Actor.
            uses_standby_mode (bool | Unset): Specifies whether the Actor will have Standby mode enabled.
     """

    actor_specification: ActorDefinitionActorSpecification
    name: str
    version: str
    build_tag: str | Unset = UNSET
    environment_variables: ActorDefinitionEnvironmentVariables | Unset = UNSET
    dockerfile: str | Unset = UNSET
    docker_context_dir: str | Unset = UNSET
    readme: str | Unset = UNSET
    input_: ActorDefinitionInput | Unset = UNSET
    changelog: str | Unset = UNSET
    storages: ActorDefinitionStorages | Unset = UNSET
    min_memory_mbytes: int | Unset = UNSET
    max_memory_mbytes: int | Unset = UNSET
    uses_standby_mode: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.actor_definition_storages import ActorDefinitionStorages
        from ..models.actor_definition_input import ActorDefinitionInput
        from ..models.actor_definition_environment_variables import ActorDefinitionEnvironmentVariables
        actor_specification = self.actor_specification.value

        name = self.name

        version = self.version

        build_tag = self.build_tag

        environment_variables: dict[str, Any] | Unset = UNSET
        if not isinstance(self.environment_variables, Unset):
            environment_variables = self.environment_variables.to_dict()

        dockerfile = self.dockerfile

        docker_context_dir = self.docker_context_dir

        readme = self.readme

        input_: dict[str, Any] | Unset = UNSET
        if not isinstance(self.input_, Unset):
            input_ = self.input_.to_dict()

        changelog = self.changelog

        storages: dict[str, Any] | Unset = UNSET
        if not isinstance(self.storages, Unset):
            storages = self.storages.to_dict()

        min_memory_mbytes = self.min_memory_mbytes

        max_memory_mbytes = self.max_memory_mbytes

        uses_standby_mode = self.uses_standby_mode


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "actorSpecification": actor_specification,
            "name": name,
            "version": version,
        })
        if build_tag is not UNSET:
            field_dict["buildTag"] = build_tag
        if environment_variables is not UNSET:
            field_dict["environmentVariables"] = environment_variables
        if dockerfile is not UNSET:
            field_dict["dockerfile"] = dockerfile
        if docker_context_dir is not UNSET:
            field_dict["dockerContextDir"] = docker_context_dir
        if readme is not UNSET:
            field_dict["readme"] = readme
        if input_ is not UNSET:
            field_dict["input"] = input_
        if changelog is not UNSET:
            field_dict["changelog"] = changelog
        if storages is not UNSET:
            field_dict["storages"] = storages
        if min_memory_mbytes is not UNSET:
            field_dict["minMemoryMbytes"] = min_memory_mbytes
        if max_memory_mbytes is not UNSET:
            field_dict["maxMemoryMbytes"] = max_memory_mbytes
        if uses_standby_mode is not UNSET:
            field_dict["usesStandbyMode"] = uses_standby_mode

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.actor_definition_storages import ActorDefinitionStorages
        from ..models.actor_definition_input import ActorDefinitionInput
        from ..models.actor_definition_environment_variables import ActorDefinitionEnvironmentVariables
        d = dict(src_dict)
        actor_specification = ActorDefinitionActorSpecification(d.pop("actorSpecification"))




        name = d.pop("name")

        version = d.pop("version")

        build_tag = d.pop("buildTag", UNSET)

        _environment_variables = d.pop("environmentVariables", UNSET)
        environment_variables: ActorDefinitionEnvironmentVariables | Unset
        if isinstance(_environment_variables,  Unset):
            environment_variables = UNSET
        else:
            environment_variables = ActorDefinitionEnvironmentVariables.from_dict(_environment_variables)




        dockerfile = d.pop("dockerfile", UNSET)

        docker_context_dir = d.pop("dockerContextDir", UNSET)

        readme = d.pop("readme", UNSET)

        _input_ = d.pop("input", UNSET)
        input_: ActorDefinitionInput | Unset
        if isinstance(_input_,  Unset):
            input_ = UNSET
        else:
            input_ = ActorDefinitionInput.from_dict(_input_)




        changelog = d.pop("changelog", UNSET)

        _storages = d.pop("storages", UNSET)
        storages: ActorDefinitionStorages | Unset
        if isinstance(_storages,  Unset):
            storages = UNSET
        else:
            storages = ActorDefinitionStorages.from_dict(_storages)




        min_memory_mbytes = d.pop("minMemoryMbytes", UNSET)

        max_memory_mbytes = d.pop("maxMemoryMbytes", UNSET)

        uses_standby_mode = d.pop("usesStandbyMode", UNSET)

        actor_definition = cls(
            actor_specification=actor_specification,
            name=name,
            version=version,
            build_tag=build_tag,
            environment_variables=environment_variables,
            dockerfile=dockerfile,
            docker_context_dir=docker_context_dir,
            readme=readme,
            input_=input_,
            changelog=changelog,
            storages=storages,
            min_memory_mbytes=min_memory_mbytes,
            max_memory_mbytes=max_memory_mbytes,
            uses_standby_mode=uses_standby_mode,
        )


        actor_definition.additional_properties = d
        return actor_definition

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
