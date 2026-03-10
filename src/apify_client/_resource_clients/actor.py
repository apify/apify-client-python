from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from pydantic import TypeAdapter

from apify_client._docs import docs_group
from apify_client._models import (
    Actor,
    ActorPermissionLevel,
    ActorResponse,
    ActorStandby,
    Build,
    BuildResponse,
    CreateOrUpdateVersionRequest,
    DefaultRunOptions,
    ExampleRunInput,
    FlatPricePerMonthActorPricingInfo,
    FreeActorPricingInfo,
    PayPerEventActorPricingInfo,
    PricePerDatasetItemActorPricingInfo,
    Run,
    RunOrigin,
    RunResponse,
    UpdateActorRequest,
)
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync
from apify_client._utils import (
    encode_key_value_store_record_value,
    encode_webhook_list_to_base64,
    response_to_dict,
    to_seconds,
)

if TYPE_CHECKING:
    from datetime import timedelta
    from decimal import Decimal
    from logging import Logger

    from apify_client._resource_clients import (
        ActorVersionClient,
        ActorVersionClientAsync,
        ActorVersionCollectionClient,
        ActorVersionCollectionClientAsync,
        BuildClient,
        BuildClientAsync,
        BuildCollectionClient,
        BuildCollectionClientAsync,
        RunClient,
        RunClientAsync,
        RunCollectionClient,
        RunCollectionClientAsync,
        WebhookCollectionClient,
        WebhookCollectionClientAsync,
    )
    from apify_client._types import ActorJobStatus, Timeout

_PricingInfo = (
    PayPerEventActorPricingInfo
    | PricePerDatasetItemActorPricingInfo
    | FlatPricePerMonthActorPricingInfo
    | FreeActorPricingInfo
)
_pricing_info_list_adapter = TypeAdapter(list[_PricingInfo])


@docs_group('Resource clients')
class ActorClient(ResourceClient):
    """Sub-client for managing a specific Actor.

    Provides methods to manage a specific Actor, e.g. update it, delete it, build it, or start runs. Obtain an instance
    via an appropriate method on the `ApifyClient` class.
    """

    def __init__(
        self,
        *,
        resource_id: str,
        resource_path: str = 'acts',
        **kwargs: Any,
    ) -> None:
        super().__init__(
            resource_id=resource_id,
            resource_path=resource_path,
            **kwargs,
        )

    def get(self, *, timeout: Timeout = 'short') -> Actor | None:
        """Retrieve the Actor.

        https://docs.apify.com/api/v2#/reference/actors/actor-object/get-actor

        Args:
            timeout: Timeout for the API HTTP request.

        Returns:
            The retrieved Actor.
        """
        result = self._get(timeout=timeout)
        if result is None:
            return None
        return ActorResponse.model_validate(result).data

    def update(
        self,
        *,
        name: str | None = None,
        title: str | None = None,
        description: str | None = None,
        seo_title: str | None = None,
        seo_description: str | None = None,
        versions: list[dict[str, Any]] | None = None,
        restart_on_error: bool | None = None,
        is_public: bool | None = None,
        is_deprecated: bool | None = None,
        categories: list[str] | None = None,
        default_run_build: str | None = None,
        default_run_max_items: int | None = None,
        default_run_memory_mbytes: int | None = None,
        default_run_timeout: timedelta | None = None,
        example_run_input_body: Any = None,
        example_run_input_content_type: str | None = None,
        actor_standby_is_enabled: bool | None = None,
        actor_standby_desired_requests_per_actor_run: int | None = None,
        actor_standby_max_requests_per_actor_run: int | None = None,
        actor_standby_idle_timeout: timedelta | None = None,
        actor_standby_build: str | None = None,
        actor_standby_memory_mbytes: int | None = None,
        pricing_infos: list[dict[str, Any]] | None = None,
        actor_permission_level: ActorPermissionLevel | None = None,
        tagged_builds: dict[str, None | dict[str, str]] | None = None,
        timeout: Timeout = 'short',
    ) -> Actor:
        """Update the Actor with the specified fields.

        https://docs.apify.com/api/v2#/reference/actors/actor-object/update-actor

        Args:
            name: The name of the Actor.
            title: The title of the Actor (human-readable).
            description: The description for the Actor.
            seo_title: The title of the Actor optimized for search engines.
            seo_description: The description of the Actor optimized for search engines.
            versions: The list of Actor versions.
            restart_on_error: If true, the Actor run process will be restarted whenever it exits with
                a non-zero status code.
            is_public: Whether the Actor is public.
            is_deprecated: Whether the Actor is deprecated.
            categories: The categories to which the Actor belongs to.
            default_run_build: Tag or number of the build that you want to run by default.
            default_run_max_items: Default limit of the number of results that will be returned
                by runs of this Actor, if the Actor is charged per result.
            default_run_memory_mbytes: Default amount of memory allocated for the runs of this Actor, in megabytes.
            default_run_timeout: Default timeout for the runs of this Actor.
            example_run_input_body: Input to be prefilled as default input to new users of this Actor.
            example_run_input_content_type: The content type of the example run input.
            actor_standby_is_enabled: Whether the Actor Standby is enabled.
            actor_standby_desired_requests_per_actor_run: The desired number of concurrent HTTP requests for
                a single Actor Standby run.
            actor_standby_max_requests_per_actor_run: The maximum number of concurrent HTTP requests for
                a single Actor Standby run.
            actor_standby_idle_timeout: If the Actor run does not receive any requests for this time,
                it will be shut down.
            actor_standby_build: The build tag or number to run when the Actor is in Standby mode.
            actor_standby_memory_mbytes: The memory in megabytes to use when the Actor is in Standby mode.
            pricing_infos: A list of objects that describes the pricing of the Actor.
            actor_permission_level: The permission level of the Actor on Apify platform.
            tagged_builds: A dictionary mapping build tag names to their settings. Use it to create, update,
                or remove build tags. To assign a tag, provide a dict with 'buildId' key. To remove a tag,
                set its value to None. Example: {'latest': {'buildId': 'abc'}, 'beta': None}.
            timeout: Timeout for the API HTTP request.

        Returns:
            The updated Actor.
        """
        actor_fields = UpdateActorRequest(
            name=name,
            title=title,
            description=description,
            seo_title=seo_title,
            seo_description=seo_description,
            versions=[CreateOrUpdateVersionRequest.model_validate(v) for v in versions] if versions else None,
            is_public=is_public,
            is_deprecated=is_deprecated,
            categories=categories,
            pricing_infos=_pricing_info_list_adapter.validate_python(pricing_infos) if pricing_infos else None,
            actor_permission_level=actor_permission_level,
            default_run_options=DefaultRunOptions(
                build=default_run_build,
                max_items=default_run_max_items,
                memory_mbytes=default_run_memory_mbytes,
                timeout_secs=to_seconds(default_run_timeout, as_int=True),
                restart_on_error=restart_on_error,
            ),
            actor_standby=ActorStandby(
                is_enabled=actor_standby_is_enabled,
                desired_requests_per_actor_run=actor_standby_desired_requests_per_actor_run,
                max_requests_per_actor_run=actor_standby_max_requests_per_actor_run,
                idle_timeout_secs=to_seconds(actor_standby_idle_timeout, as_int=True),
                build=actor_standby_build,
                memory_mbytes=actor_standby_memory_mbytes,
            ),
            example_run_input=ExampleRunInput(
                body=example_run_input_body,
                content_type=example_run_input_content_type,
            ),
            tagged_builds=tagged_builds,
        )
        result = self._update(timeout=timeout, **actor_fields.model_dump(by_alias=True, exclude_none=True))
        return ActorResponse.model_validate(result).data

    def delete(self, *, timeout: Timeout = 'short') -> None:
        """Delete the Actor.

        https://docs.apify.com/api/v2#/reference/actors/actor-object/delete-actor

        Args:
            timeout: Timeout for the API HTTP request.
        """
        self._delete(timeout=timeout)

    def start(
        self,
        *,
        run_input: Any = None,
        content_type: str | None = None,
        build: str | None = None,
        max_items: int | None = None,
        max_total_charge_usd: Decimal | None = None,
        restart_on_error: bool | None = None,
        memory_mbytes: int | None = None,
        run_timeout: timedelta | None = None,
        force_permission_level: ActorPermissionLevel | None = None,
        wait_for_finish: int | None = None,
        webhooks: list[dict] | None = None,
        timeout: Timeout = 'medium',
    ) -> Run:
        """Start the Actor and immediately return the Run object.

        https://docs.apify.com/api/v2#/reference/actors/run-collection/run-actor

        Args:
            run_input: The input to pass to the Actor run.
            content_type: The content type of the input.
            build: Specifies the Actor build to run. It can be either a build tag or build number. By default,
                the run uses the build specified in the default run configuration for the Actor (typically latest).
            max_items: Maximum number of results that will be returned by this run. If the Actor is charged
                per result, you will not be charged for more results than the given limit.
            max_total_charge_usd: A limit on the total charged amount for pay-per-event Actors.
            restart_on_error: If true, the Actor run process will be restarted whenever it exits with
                a non-zero status code.
            memory_mbytes: Memory limit for the run, in megabytes. By default, the run uses a memory limit
                specified in the default run configuration for the Actor.
            run_timeout: Optional timeout for the run. By default, the run uses timeout specified
                in the default run configuration for the Actor.
            force_permission_level: Override the Actor's permissions for this run. If not set, the Actor will run
                with permissions configured in the Actor settings.
            wait_for_finish: The maximum number of seconds the server waits for the run to finish. By default,
                it is 0, the maximum value is 60.
            webhooks: Optional ad-hoc webhooks (https://docs.apify.com/webhooks/ad-hoc-webhooks) associated with
                the Actor run which can be used to receive a notification, e.g. when the Actor finished or failed.
                If you already have a webhook set up for the Actor or task, you do not have to add it again here.
                Each webhook is represented by a dictionary containing these items:
                    * `event_types`: List of `WebhookEventType` values which trigger the webhook.
                    * `request_url`: URL to which to send the webhook HTTP request.
                    * `payload_template`: Optional template for the request payload.
            timeout: Timeout for the API HTTP request.

        Returns:
            The run object.
        """
        run_input, content_type = encode_key_value_store_record_value(run_input, content_type)

        request_params = self._build_params(
            build=build,
            maxItems=max_items,
            maxTotalChargeUsd=max_total_charge_usd,
            restartOnError=restart_on_error,
            memory=memory_mbytes,
            timeout=to_seconds(run_timeout, as_int=True),
            waitForFinish=wait_for_finish,
            forcePermissionLevel=force_permission_level.value if force_permission_level is not None else None,
            webhooks=encode_webhook_list_to_base64(webhooks) if webhooks is not None else None,
        )

        response = self._http_client.call(
            url=self._build_url('runs'),
            method='POST',
            headers={'content-type': content_type},
            data=run_input,
            params=request_params,
            timeout=timeout,
        )

        result = response_to_dict(response)
        return RunResponse.model_validate(result).data

    def call(
        self,
        *,
        run_input: Any = None,
        content_type: str | None = None,
        build: str | None = None,
        max_items: int | None = None,
        max_total_charge_usd: Decimal | None = None,
        restart_on_error: bool | None = None,
        memory_mbytes: int | None = None,
        run_timeout: timedelta | None = None,
        webhooks: list[dict] | None = None,
        force_permission_level: ActorPermissionLevel | None = None,
        wait_duration: timedelta | None = None,
        logger: Logger | None | Literal['default'] = 'default',
        timeout: Timeout = 'no_timeout',
    ) -> Run | None:
        """Start the Actor and wait for it to finish before returning the Run object.

        It waits indefinitely, unless the wait_duration argument is provided.

        https://docs.apify.com/api/v2#/reference/actors/run-collection/run-actor

        Args:
            run_input: The input to pass to the Actor run.
            content_type: The content type of the input.
            build: Specifies the Actor build to run. It can be either a build tag or build number. By default,
                the run uses the build specified in the default run configuration for the Actor (typically latest).
            max_items: Maximum number of results that will be returned by this run. If the Actor is charged
                per result, you will not be charged for more results than the given limit.
            max_total_charge_usd: A limit on the total charged amount for pay-per-event Actors.
            restart_on_error: If true, the Actor run process will be restarted whenever it exits with
                a non-zero status code.
            memory_mbytes: Memory limit for the run, in megabytes. By default, the run uses a memory limit
                specified in the default run configuration for the Actor.
            run_timeout: Optional timeout for the run. By default, the run uses timeout specified
                in the default run configuration for the Actor.
            force_permission_level: Override the Actor's permissions for this run. If not set, the Actor will run
                with permissions configured in the Actor settings.
            webhooks: Optional webhooks (https://docs.apify.com/webhooks) associated with the Actor run, which can
                be used to receive a notification, e.g. when the Actor finished or failed. If you already have
                a webhook set up for the Actor, you do not have to add it again here.
            wait_duration: The maximum time the server waits for the run to finish. If not provided,
                waits indefinitely.
            logger: Logger used to redirect logs from the Actor run. Using "default" literal means that a predefined
                default logger will be used. Setting `None` will disable any log propagation. Passing custom logger
                will redirect logs to the provided logger. The logger is also used to capture status and status message
                of the other Actor run.
            timeout: Timeout for the API HTTP request.

        Returns:
            The run object.
        """
        started_run = self.start(
            run_input=run_input,
            content_type=content_type,
            build=build,
            max_items=max_items,
            max_total_charge_usd=max_total_charge_usd,
            restart_on_error=restart_on_error,
            memory_mbytes=memory_mbytes,
            run_timeout=run_timeout,
            webhooks=webhooks,
            force_permission_level=force_permission_level,
            timeout=timeout,
        )
        run_client = self._client_registry.run_client(
            resource_id=started_run.id,
            base_url=self._base_url,
            public_base_url=self._public_base_url,
            http_client=self._http_client,
            client_registry=self._client_registry,
        )

        if not logger:
            return run_client.wait_for_finish(wait_duration=wait_duration)

        if logger == 'default':
            logger = None

        with run_client.get_status_message_watcher(to_logger=logger), run_client.get_streamed_log(to_logger=logger):
            return run_client.wait_for_finish(wait_duration=wait_duration)

    def build(
        self,
        *,
        version_number: str,
        beta_packages: bool | None = None,
        tag: str | None = None,
        use_cache: bool | None = None,
        wait_for_finish: int | None = None,
        timeout: Timeout = 'medium',
    ) -> Build:
        """Build the Actor.

        https://docs.apify.com/api/v2#/reference/actors/build-collection/build-actor

        Args:
            version_number: Actor version number to be built.
            beta_packages: If True, then the Actor is built with beta versions of Apify NPM packages. By default,
                the build uses latest stable packages.
            tag: Tag to be applied to the build on success. By default, the tag is taken from the Actor version's
                build tag property.
            use_cache: If true, the Actor's Docker container will be rebuilt using layer cache
                (https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#leverage-build-cache).
                This is to enable quick rebuild during development. By default, the cache is not used.
            wait_for_finish: The maximum number of seconds the server waits for the build to finish before returning.
                By default it is 0, the maximum value is 60.
            timeout: Timeout for the API HTTP request.

        Returns:
            The build object.
        """
        request_params = self._build_params(
            version=version_number,
            betaPackages=beta_packages,
            tag=tag,
            useCache=use_cache,
            waitForFinish=wait_for_finish,
        )

        response = self._http_client.call(
            url=self._build_url('builds'),
            method='POST',
            params=request_params,
            timeout=timeout,
        )

        result = response_to_dict(response)
        return BuildResponse.model_validate(result).data

    def builds(self) -> BuildCollectionClient:
        """Retrieve a client for the builds of this Actor."""
        return self._client_registry.build_collection_client(
            resource_path='builds',
            **self._base_client_kwargs,
        )

    def runs(self) -> RunCollectionClient:
        """Retrieve a client for the runs of this Actor."""
        return self._client_registry.run_collection_client(
            resource_path='runs',
            **self._base_client_kwargs,
        )

    def default_build(
        self,
        *,
        wait_for_finish: int | None = None,
        timeout: Timeout = 'short',
    ) -> BuildClient:
        """Retrieve Actor's default build.

        https://docs.apify.com/api/v2/act-build-default-get

        Args:
            wait_for_finish: The maximum number of seconds the server waits for the build to finish before returning.
                By default it is 0, the maximum value is 60.
            timeout: Timeout for the API HTTP request.

        Returns:
            The resource client for the default build of this Actor.
        """
        request_params = self._build_params(
            waitForFinish=wait_for_finish,
        )

        response = self._http_client.call(
            url=self._build_url('builds/default'),
            method='GET',
            params=request_params,
            timeout=timeout,
        )
        result = response_to_dict(response)

        return self._client_registry.build_client(
            resource_id=result['data']['id'],
            base_url=self._base_url,
            public_base_url=self._public_base_url,
            http_client=self._http_client,
            client_registry=self._client_registry,
        )

    def last_run(
        self,
        *,
        status: ActorJobStatus | None = None,
        origin: RunOrigin | None = None,
    ) -> RunClient:
        """Retrieve the client for the last run of this Actor.

        Last run is retrieved based on the start time of the runs.

        Args:
            status: Consider only runs with this status.
            origin: Consider only runs started with this origin.

        Returns:
            The resource client for the last run of this Actor.
        """
        return self._client_registry.run_client(
            resource_id='last',
            resource_path='runs',
            params=self._build_params(
                status=status,
                origin=origin,
            ),
            **self._base_client_kwargs,
        )

    def versions(self) -> ActorVersionCollectionClient:
        """Retrieve a client for the versions of this Actor."""
        return self._client_registry.actor_version_collection_client(**self._base_client_kwargs)

    def version(self, version_number: str) -> ActorVersionClient:
        """Retrieve the client for the specified version of this Actor.

        Args:
            version_number: The version number for which to retrieve the resource client.

        Returns:
            The resource client for the specified Actor version.
        """
        return self._client_registry.actor_version_client(
            resource_id=version_number,
            **self._base_client_kwargs,
        )

    def webhooks(self) -> WebhookCollectionClient:
        """Retrieve a client for webhooks associated with this Actor."""
        return self._client_registry.webhook_collection_client(**self._base_client_kwargs)

    def validate_input(
        self,
        run_input: Any = None,
        *,
        build_tag: str | None = None,
        content_type: str | None = None,
        timeout: Timeout = 'short',
    ) -> bool:
        """Validate an input for the Actor that defines an input schema.

        Args:
            run_input: The input to validate.
            build_tag: The Actor's build tag.
            content_type: The content type of the input.
            timeout: Timeout for the API HTTP request.

        Returns:
            True if the input is valid, else raise an exception with validation error details.
        """
        run_input, content_type = encode_key_value_store_record_value(run_input, content_type)

        self._http_client.call(
            url=self._build_url('validate-input'),
            method='POST',
            headers={'content-type': content_type},
            data=run_input,
            params=self._build_params(build=build_tag),
            timeout=timeout,
        )

        return True


@docs_group('Resource clients')
class ActorClientAsync(ResourceClientAsync):
    """Sub-client for managing a specific Actor.

    Provides methods to manage a specific Actor, e.g. update it, delete it, build it, or start runs. Obtain an instance
    via an appropriate method on the `ApifyClientAsync` class.
    """

    def __init__(
        self,
        *,
        resource_id: str,
        resource_path: str = 'acts',
        **kwargs: Any,
    ) -> None:
        super().__init__(
            resource_id=resource_id,
            resource_path=resource_path,
            **kwargs,
        )

    async def get(self, *, timeout: Timeout = 'short') -> Actor | None:
        """Retrieve the Actor.

        https://docs.apify.com/api/v2#/reference/actors/actor-object/get-actor

        Args:
            timeout: Timeout for the API HTTP request.

        Returns:
            The retrieved Actor.
        """
        result = await self._get(timeout=timeout)
        if result is None:
            return None
        return ActorResponse.model_validate(result).data

    async def update(
        self,
        *,
        name: str | None = None,
        title: str | None = None,
        description: str | None = None,
        seo_title: str | None = None,
        seo_description: str | None = None,
        versions: list[dict[str, Any]] | None = None,
        restart_on_error: bool | None = None,
        is_public: bool | None = None,
        is_deprecated: bool | None = None,
        categories: list[str] | None = None,
        default_run_build: str | None = None,
        default_run_max_items: int | None = None,
        default_run_memory_mbytes: int | None = None,
        default_run_timeout: timedelta | None = None,
        example_run_input_body: Any = None,
        example_run_input_content_type: str | None = None,
        actor_standby_is_enabled: bool | None = None,
        actor_standby_desired_requests_per_actor_run: int | None = None,
        actor_standby_max_requests_per_actor_run: int | None = None,
        actor_standby_idle_timeout: timedelta | None = None,
        actor_standby_build: str | None = None,
        actor_standby_memory_mbytes: int | None = None,
        pricing_infos: list[dict[str, Any]] | None = None,
        actor_permission_level: ActorPermissionLevel | None = None,
        tagged_builds: dict[str, None | dict[str, str]] | None = None,
        timeout: Timeout = 'short',
    ) -> Actor:
        """Update the Actor with the specified fields.

        https://docs.apify.com/api/v2#/reference/actors/actor-object/update-actor

        Args:
            name: The name of the Actor.
            title: The title of the Actor (human-readable).
            description: The description for the Actor.
            seo_title: The title of the Actor optimized for search engines.
            seo_description: The description of the Actor optimized for search engines.
            versions: The list of Actor versions.
            restart_on_error: If true, the Actor run process will be restarted whenever it exits with
                a non-zero status code.
            is_public: Whether the Actor is public.
            is_deprecated: Whether the Actor is deprecated.
            categories: The categories to which the Actor belongs to.
            default_run_build: Tag or number of the build that you want to run by default.
            default_run_max_items: Default limit of the number of results that will be returned
                by runs of this Actor, if the Actor is charged per result.
            default_run_memory_mbytes: Default amount of memory allocated for the runs of this Actor, in megabytes.
            default_run_timeout: Default timeout for the runs of this Actor.
            example_run_input_body: Input to be prefilled as default input to new users of this Actor.
            example_run_input_content_type: The content type of the example run input.
            actor_standby_is_enabled: Whether the Actor Standby is enabled.
            actor_standby_desired_requests_per_actor_run: The desired number of concurrent HTTP requests for
                a single Actor Standby run.
            actor_standby_max_requests_per_actor_run: The maximum number of concurrent HTTP requests for
                a single Actor Standby run.
            actor_standby_idle_timeout: If the Actor run does not receive any requests for this time,
                it will be shut down.
            actor_standby_build: The build tag or number to run when the Actor is in Standby mode.
            actor_standby_memory_mbytes: The memory in megabytes to use when the Actor is in Standby mode.
            pricing_infos: A list of objects that describes the pricing of the Actor.
            actor_permission_level: The permission level of the Actor on Apify platform.
            tagged_builds: A dictionary mapping build tag names to their settings. Use it to create, update,
                or remove build tags. To assign a tag, provide a dict with 'buildId' key. To remove a tag,
                set its value to None. Example: {'latest': {'buildId': 'abc'}, 'beta': None}.
            timeout: Timeout for the API HTTP request.

        Returns:
            The updated Actor.
        """
        actor_fields = UpdateActorRequest(
            name=name,
            title=title,
            description=description,
            seo_title=seo_title,
            seo_description=seo_description,
            versions=[CreateOrUpdateVersionRequest.model_validate(v) for v in versions] if versions else None,
            is_public=is_public,
            is_deprecated=is_deprecated,
            categories=categories,
            pricing_infos=_pricing_info_list_adapter.validate_python(pricing_infos) if pricing_infos else None,
            actor_permission_level=actor_permission_level,
            default_run_options=DefaultRunOptions(
                build=default_run_build,
                max_items=default_run_max_items,
                memory_mbytes=default_run_memory_mbytes,
                timeout_secs=to_seconds(default_run_timeout, as_int=True),
                restart_on_error=restart_on_error,
            ),
            actor_standby=ActorStandby(
                is_enabled=actor_standby_is_enabled,
                desired_requests_per_actor_run=actor_standby_desired_requests_per_actor_run,
                max_requests_per_actor_run=actor_standby_max_requests_per_actor_run,
                idle_timeout_secs=to_seconds(actor_standby_idle_timeout, as_int=True),
                build=actor_standby_build,
                memory_mbytes=actor_standby_memory_mbytes,
            ),
            example_run_input=ExampleRunInput(
                body=example_run_input_body,
                content_type=example_run_input_content_type,
            ),
            tagged_builds=tagged_builds,
        )
        result = await self._update(timeout=timeout, **actor_fields.model_dump(by_alias=True, exclude_none=True))
        return ActorResponse.model_validate(result).data

    async def delete(self, *, timeout: Timeout = 'short') -> None:
        """Delete the Actor.

        https://docs.apify.com/api/v2#/reference/actors/actor-object/delete-actor

        Args:
            timeout: Timeout for the API HTTP request.
        """
        await self._delete(timeout=timeout)

    async def start(
        self,
        *,
        run_input: Any = None,
        content_type: str | None = None,
        build: str | None = None,
        max_items: int | None = None,
        max_total_charge_usd: Decimal | None = None,
        restart_on_error: bool | None = None,
        memory_mbytes: int | None = None,
        run_timeout: timedelta | None = None,
        force_permission_level: ActorPermissionLevel | None = None,
        wait_for_finish: int | None = None,
        webhooks: list[dict] | None = None,
        timeout: Timeout = 'medium',
    ) -> Run:
        """Start the Actor and immediately return the Run object.

        https://docs.apify.com/api/v2#/reference/actors/run-collection/run-actor

        Args:
            run_input: The input to pass to the Actor run.
            content_type: The content type of the input.
            build: Specifies the Actor build to run. It can be either a build tag or build number. By default,
                the run uses the build specified in the default run configuration for the Actor (typically latest).
            max_items: Maximum number of results that will be returned by this run. If the Actor is charged
                per result, you will not be charged for more results than the given limit.
            max_total_charge_usd: A limit on the total charged amount for pay-per-event Actors.
            restart_on_error: If true, the Actor run process will be restarted whenever it exits with
                a non-zero status code.
            memory_mbytes: Memory limit for the run, in megabytes. By default, the run uses a memory limit
                specified in the default run configuration for the Actor.
            run_timeout: Optional timeout for the run. By default, the run uses timeout specified
                in the default run configuration for the Actor.
            force_permission_level: Override the Actor's permissions for this run. If not set, the Actor will run
                with permissions configured in the Actor settings.
            wait_for_finish: The maximum number of seconds the server waits for the run to finish. By default,
                it is 0, the maximum value is 60.
            webhooks: Optional ad-hoc webhooks (https://docs.apify.com/webhooks/ad-hoc-webhooks) associated with
                the Actor run which can be used to receive a notification, e.g. when the Actor finished or failed.
                If you already have a webhook set up for the Actor or task, you do not have to add it again here.
                Each webhook is represented by a dictionary containing these items:
                    * `event_types`: List of `WebhookEventType` values which trigger the webhook.
                    * `request_url`: URL to which to send the webhook HTTP request.
                    * `payload_template`: Optional template for the request payload.
            timeout: Timeout for the API HTTP request.

        Returns:
            The run object.
        """
        run_input, content_type = encode_key_value_store_record_value(run_input, content_type)

        request_params = self._build_params(
            build=build,
            maxItems=max_items,
            maxTotalChargeUsd=max_total_charge_usd,
            restartOnError=restart_on_error,
            memory=memory_mbytes,
            timeout=to_seconds(run_timeout, as_int=True),
            waitForFinish=wait_for_finish,
            forcePermissionLevel=force_permission_level.value if force_permission_level is not None else None,
            webhooks=encode_webhook_list_to_base64(webhooks) if webhooks is not None else None,
        )

        response = await self._http_client.call(
            url=self._build_url('runs'),
            method='POST',
            headers={'content-type': content_type},
            data=run_input,
            params=request_params,
            timeout=timeout,
        )

        result = response_to_dict(response)
        return RunResponse.model_validate(result).data

    async def call(
        self,
        *,
        run_input: Any = None,
        content_type: str | None = None,
        build: str | None = None,
        max_items: int | None = None,
        max_total_charge_usd: Decimal | None = None,
        restart_on_error: bool | None = None,
        memory_mbytes: int | None = None,
        run_timeout: timedelta | None = None,
        webhooks: list[dict] | None = None,
        force_permission_level: ActorPermissionLevel | None = None,
        wait_duration: timedelta | None = None,
        logger: Logger | None | Literal['default'] = 'default',
        timeout: Timeout = 'no_timeout',
    ) -> Run | None:
        """Start the Actor and wait for it to finish before returning the Run object.

        It waits indefinitely, unless the wait_duration argument is provided.

        https://docs.apify.com/api/v2#/reference/actors/run-collection/run-actor

        Args:
            run_input: The input to pass to the Actor run.
            content_type: The content type of the input.
            build: Specifies the Actor build to run. It can be either a build tag or build number. By default,
                the run uses the build specified in the default run configuration for the Actor (typically latest).
            max_items: Maximum number of results that will be returned by this run. If the Actor is charged
                per result, you will not be charged for more results than the given limit.
            max_total_charge_usd: A limit on the total charged amount for pay-per-event Actors.
            restart_on_error: If true, the Actor run process will be restarted whenever it exits with
                a non-zero status code.
            memory_mbytes: Memory limit for the run, in megabytes. By default, the run uses a memory limit
                specified in the default run configuration for the Actor.
            run_timeout: Optional timeout for the run. By default, the run uses timeout specified
                in the default run configuration for the Actor.
            force_permission_level: Override the Actor's permissions for this run. If not set, the Actor will run
                with permissions configured in the Actor settings.
            webhooks: Optional webhooks (https://docs.apify.com/webhooks) associated with the Actor run, which can
                be used to receive a notification, e.g. when the Actor finished or failed. If you already have
                a webhook set up for the Actor, you do not have to add it again here.
            wait_duration: The maximum time the server waits for the run to finish. If not provided,
                waits indefinitely.
            logger: Logger used to redirect logs from the Actor run. Using "default" literal means that a predefined
                default logger will be used. Setting `None` will disable any log propagation. Passing custom logger
                will redirect logs to the provided logger. The logger is also used to capture status and status message
                of the other Actor run.
            timeout: Timeout for the API HTTP request.

        Returns:
            The run object.
        """
        started_run = await self.start(
            run_input=run_input,
            content_type=content_type,
            build=build,
            max_items=max_items,
            max_total_charge_usd=max_total_charge_usd,
            restart_on_error=restart_on_error,
            memory_mbytes=memory_mbytes,
            run_timeout=run_timeout,
            webhooks=webhooks,
            force_permission_level=force_permission_level,
            timeout=timeout,
        )

        run_client = self._client_registry.run_client(
            resource_id=started_run.id,
            base_url=self._base_url,
            public_base_url=self._public_base_url,
            http_client=self._http_client,
            client_registry=self._client_registry,
        )

        if not logger:
            return await run_client.wait_for_finish(wait_duration=wait_duration)

        if logger == 'default':
            logger = None

        status_redirector = await run_client.get_status_message_watcher(to_logger=logger)
        streamed_log = await run_client.get_streamed_log(to_logger=logger)

        async with status_redirector, streamed_log:
            return await run_client.wait_for_finish(wait_duration=wait_duration)

    async def build(
        self,
        *,
        version_number: str,
        beta_packages: bool | None = None,
        tag: str | None = None,
        use_cache: bool | None = None,
        wait_for_finish: int | None = None,
        timeout: Timeout = 'medium',
    ) -> Build:
        """Build the Actor.

        https://docs.apify.com/api/v2#/reference/actors/build-collection/build-actor

        Args:
            version_number: Actor version number to be built.
            beta_packages: If True, then the Actor is built with beta versions of Apify NPM packages. By default,
                the build uses latest stable packages.
            tag: Tag to be applied to the build on success. By default, the tag is taken from the Actor version's
                build tag property.
            use_cache: If true, the Actor's Docker container will be rebuilt using layer cache
                (https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#leverage-build-cache).
                This is to enable quick rebuild during development. By default, the cache is not used.
            wait_for_finish: The maximum number of seconds the server waits for the build to finish before returning.
                By default it is 0, the maximum value is 60.
            timeout: Timeout for the API HTTP request.

        Returns:
            The build object.
        """
        request_params = self._build_params(
            version=version_number,
            betaPackages=beta_packages,
            tag=tag,
            useCache=use_cache,
            waitForFinish=wait_for_finish,
        )

        response = await self._http_client.call(
            url=self._build_url('builds'),
            method='POST',
            params=request_params,
            timeout=timeout,
        )

        result = response_to_dict(response)
        return BuildResponse.model_validate(result).data

    def builds(self) -> BuildCollectionClientAsync:
        """Retrieve a client for the builds of this Actor."""
        return self._client_registry.build_collection_client(
            resource_path='builds',
            **self._base_client_kwargs,
        )

    def runs(self) -> RunCollectionClientAsync:
        """Retrieve a client for the runs of this Actor."""
        return self._client_registry.run_collection_client(
            resource_path='runs',
            **self._base_client_kwargs,
        )

    async def default_build(
        self,
        *,
        wait_for_finish: int | None = None,
        timeout: Timeout = 'short',
    ) -> BuildClientAsync:
        """Retrieve Actor's default build.

        https://docs.apify.com/api/v2/act-build-default-get

        Args:
            wait_for_finish: The maximum number of seconds the server waits for the build to finish before returning.
                By default it is 0, the maximum value is 60.
            timeout: Timeout for the API HTTP request.

        Returns:
            The resource client for the default build of this Actor.
        """
        request_params = self._build_params(
            waitForFinish=wait_for_finish,
        )

        response = await self._http_client.call(
            url=self._build_url('builds/default'),
            method='GET',
            params=request_params,
            timeout=timeout,
        )
        result = response_to_dict(response)

        return self._client_registry.build_client(
            resource_id=result['data']['id'],
            base_url=self._base_url,
            public_base_url=self._public_base_url,
            http_client=self._http_client,
            client_registry=self._client_registry,
        )

    def last_run(
        self,
        *,
        status: ActorJobStatus | None = None,
        origin: RunOrigin | None = None,
    ) -> RunClientAsync:
        """Retrieve the client for the last run of this Actor.

        Last run is retrieved based on the start time of the runs.

        Args:
            status: Consider only runs with this status.
            origin: Consider only runs started with this origin.

        Returns:
            The resource client for the last run of this Actor.
        """
        return self._client_registry.run_client(
            resource_id='last',
            resource_path='runs',
            params=self._build_params(
                status=status,
                origin=origin,
            ),
            **self._base_client_kwargs,
        )

    def versions(self) -> ActorVersionCollectionClientAsync:
        """Retrieve a client for the versions of this Actor."""
        return self._client_registry.actor_version_collection_client(**self._base_client_kwargs)

    def version(self, version_number: str) -> ActorVersionClientAsync:
        """Retrieve the client for the specified version of this Actor.

        Args:
            version_number: The version number for which to retrieve the resource client.

        Returns:
            The resource client for the specified Actor version.
        """
        return self._client_registry.actor_version_client(
            resource_id=version_number,
            **self._base_client_kwargs,
        )

    def webhooks(self) -> WebhookCollectionClientAsync:
        """Retrieve a client for webhooks associated with this Actor."""
        return self._client_registry.webhook_collection_client(**self._base_client_kwargs)

    async def validate_input(
        self,
        run_input: Any = None,
        *,
        build_tag: str | None = None,
        content_type: str | None = None,
        timeout: Timeout = 'short',
    ) -> bool:
        """Validate an input for the Actor that defines an input schema.

        Args:
            run_input: The input to validate.
            build_tag: The Actor's build tag.
            content_type: The content type of the input.
            timeout: Timeout for the API HTTP request.

        Returns:
            True if the input is valid, else raise an exception with validation error details.
        """
        run_input, content_type = encode_key_value_store_record_value(run_input, content_type)

        await self._http_client.call(
            url=self._build_url('validate-input'),
            method='POST',
            headers={'content-type': content_type},
            data=run_input,
            params=self._build_params(build=build_tag),
            timeout=timeout,
        )

        return True
