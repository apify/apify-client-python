from __future__ import annotations

from typing import TYPE_CHECKING, Any

from apify_shared.utils import (
    filter_out_none_values_recursively,
    ignore_docs,
    maybe_extract_enum_member_value,
    parse_date_fields,
)

from apify_client._utils import encode_key_value_store_record_value, encode_webhook_list_to_base64, pluck_data
from apify_client.clients.base import ResourceClient, ResourceClientAsync
from apify_client.clients.resource_clients.actor_version import ActorVersionClient, ActorVersionClientAsync
from apify_client.clients.resource_clients.actor_version_collection import ActorVersionCollectionClient, ActorVersionCollectionClientAsync
from apify_client.clients.resource_clients.build_collection import BuildCollectionClient, BuildCollectionClientAsync
from apify_client.clients.resource_clients.run import RunClient, RunClientAsync
from apify_client.clients.resource_clients.run_collection import RunCollectionClient, RunCollectionClientAsync
from apify_client.clients.resource_clients.webhook_collection import WebhookCollectionClient, WebhookCollectionClientAsync

if TYPE_CHECKING:
    from apify_shared.consts import ActorJobStatus, MetaOrigin


def get_actor_representation(
    *,
    name: str | None,
    title: str | None = None,
    description: str | None = None,
    seo_title: str | None = None,
    seo_description: str | None = None,
    versions: list[dict] | None = None,
    restart_on_error: bool | None = None,
    is_public: bool | None = None,
    is_deprecated: bool | None = None,
    is_anonymously_runnable: bool | None = None,
    categories: list[str] | None = None,
    default_run_build: str | None = None,
    default_run_max_items: int | None = None,
    default_run_memory_mbytes: int | None = None,
    default_run_timeout_secs: int | None = None,
    example_run_input_body: Any = None,
    example_run_input_content_type: str | None = None,
    actor_standby_is_enabled: bool | None = None,
    actor_standby_desired_requests_per_actor_run: int | None = None,
    actor_standby_max_requests_per_actor_run: int | None = None,
    actor_standby_idle_timeout_secs: int | None = None,
    actor_standby_build: str | None = None,
    actor_standby_memory_mbytes: int | None = None,
) -> dict:
    """Get dictionary representation of the Actor."""
    return {
        'name': name,
        'title': title,
        'description': description,
        'seoTitle': seo_title,
        'seoDescription': seo_description,
        'versions': versions,
        'restartOnError': restart_on_error,
        'isPublic': is_public,
        'isDeprecated': is_deprecated,
        'isAnonymouslyRunnable': is_anonymously_runnable,
        'categories': categories,
        'defaultRunOptions': {
            'build': default_run_build,
            'maxItems': default_run_max_items,
            'memoryMbytes': default_run_memory_mbytes,
            'timeoutSecs': default_run_timeout_secs,
        },
        'exampleRunInput': {
            'body': example_run_input_body,
            'contentType': example_run_input_content_type,
        },
        'actorStandby': {
            'isEnabled': actor_standby_is_enabled,
            'desiredRequestsPerActorRun': actor_standby_desired_requests_per_actor_run,
            'maxRequestsPerActorRun': actor_standby_max_requests_per_actor_run,
            'idleTimeoutSecs': actor_standby_idle_timeout_secs,
            'build': actor_standby_build,
            'memoryMbytes': actor_standby_memory_mbytes,
        },
    }


class ActorClient(ResourceClient):
    """Sub-client for manipulating a single Actor."""

    @ignore_docs
    def __init__(self: ActorClient, *args: Any, **kwargs: Any) -> None:
        """Initialize the ActorClient."""
        resource_path = kwargs.pop('resource_path', 'acts')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def get(self: ActorClient) -> dict | None:
        """Retrieve the Actor.

        https://docs.apify.com/api/v2#/reference/actors/actor-object/get-actor

        Returns:
            dict, optional: The retrieved Actor
        """
        return self._get()

    def update(
        self: ActorClient,
        *,
        name: str | None = None,
        title: str | None = None,
        description: str | None = None,
        seo_title: str | None = None,
        seo_description: str | None = None,
        versions: list[dict] | None = None,
        restart_on_error: bool | None = None,
        is_public: bool | None = None,
        is_deprecated: bool | None = None,
        is_anonymously_runnable: bool | None = None,
        categories: list[str] | None = None,
        default_run_build: str | None = None,
        default_run_max_items: int | None = None,
        default_run_memory_mbytes: int | None = None,
        default_run_timeout_secs: int | None = None,
        example_run_input_body: Any = None,
        example_run_input_content_type: str | None = None,
        actor_standby_is_enabled: bool | None = None,
        actor_standby_desired_requests_per_actor_run: int | None = None,
        actor_standby_max_requests_per_actor_run: int | None = None,
        actor_standby_idle_timeout_secs: int | None = None,
        actor_standby_build: str | None = None,
        actor_standby_memory_mbytes: int | None = None,
    ) -> dict:
        """Update the Actor with the specified fields.

        https://docs.apify.com/api/v2#/reference/actors/actor-object/update-actor

        Args:
            name (str, optional): The name of the Actor
            title (str, optional): The title of the Actor (human-readable)
            description (str, optional): The description for the Actor
            seo_title (str, optional): The title of the Actor optimized for search engines
            seo_description (str, optional): The description of the Actor optimized for search engines
            versions (list of dict, optional): The list of Actor versions
            restart_on_error (bool, optional): If true, the main Actor run process will be restarted whenever it exits with a non-zero status code.
            is_public (bool, optional): Whether the Actor is public.
            is_deprecated (bool, optional): Whether the Actor is deprecated.
            is_anonymously_runnable (bool, optional): Whether the Actor is anonymously runnable.
            categories (list of str, optional): The categories to which the Actor belongs to.
            default_run_build (str, optional): Tag or number of the build that you want to run by default.
            default_run_max_items (int, optional): Default limit of the number of results that will be returned by runs of this Actor,
                                                   if the Actor is charged per result.
            default_run_memory_mbytes (int, optional): Default amount of memory allocated for the runs of this Actor, in megabytes.
            default_run_timeout_secs (int, optional): Default timeout for the runs of this Actor in seconds.
            example_run_input_body (Any, optional): Input to be prefilled as default input to new users of this Actor.
            example_run_input_content_type (str, optional): The content type of the example run input.
            actor_standby_is_enabled (bool, optional): Whether the Actor Standby is enabled.
            actor_standby_desired_requests_per_actor_run (int, optional): The desired number of concurrent HTTP requests for
                a single Actor Standby run.
            actor_standby_max_requests_per_actor_run (int, optional): The maximum number of concurrent HTTP requests for a single Actor Standby run.
            actor_standby_idle_timeout_secs (int, optional): If the Actor run does not receive any requests for this time, it will be shut down.
            actor_standby_build (str, optional): The build tag or number to run when the Actor is in Standby mode.
            actor_standby_memory_mbytes (int, optional): The memory in megabytes to use when the Actor is in Standby mode.

        Returns:
            dict: The updated Actor
        """
        actor_representation = get_actor_representation(
            name=name,
            title=title,
            description=description,
            seo_title=seo_title,
            seo_description=seo_description,
            versions=versions,
            restart_on_error=restart_on_error,
            is_public=is_public,
            is_deprecated=is_deprecated,
            is_anonymously_runnable=is_anonymously_runnable,
            categories=categories,
            default_run_build=default_run_build,
            default_run_max_items=default_run_max_items,
            default_run_memory_mbytes=default_run_memory_mbytes,
            default_run_timeout_secs=default_run_timeout_secs,
            example_run_input_body=example_run_input_body,
            example_run_input_content_type=example_run_input_content_type,
            actor_standby_is_enabled=actor_standby_is_enabled,
            actor_standby_desired_requests_per_actor_run=actor_standby_desired_requests_per_actor_run,
            actor_standby_max_requests_per_actor_run=actor_standby_max_requests_per_actor_run,
            actor_standby_idle_timeout_secs=actor_standby_idle_timeout_secs,
            actor_standby_build=actor_standby_build,
            actor_standby_memory_mbytes=actor_standby_memory_mbytes,
        )

        return self._update(filter_out_none_values_recursively(actor_representation))

    def delete(self: ActorClient) -> None:
        """Delete the Actor.

        https://docs.apify.com/api/v2#/reference/actors/actor-object/delete-actor
        """
        return self._delete()

    def start(
        self: ActorClient,
        *,
        run_input: Any = None,
        content_type: str | None = None,
        build: str | None = None,
        max_items: int | None = None,
        memory_mbytes: int | None = None,
        timeout_secs: int | None = None,
        wait_for_finish: int | None = None,
        webhooks: list[dict] | None = None,
    ) -> dict:
        """Start the Actor and immediately return the Run object.

        https://docs.apify.com/api/v2#/reference/actors/run-collection/run-actor

        Args:
            run_input (Any, optional): The input to pass to the Actor run.
            content_type (str, optional): The content type of the input.
            build (str, optional): Specifies the Actor build to run. It can be either a build tag or build number.
                                   By default, the run uses the build specified in the default run configuration for the Actor (typically latest).
            max_items (int, optional): Maximum number of results that will be returned by this run.
                                       If the Actor is charged per result, you will not be charged for more results than the given limit.
            memory_mbytes (int, optional): Memory limit for the run, in megabytes.
                                           By default, the run uses a memory limit specified in the default run configuration for the Actor.
            timeout_secs (int, optional): Optional timeout for the run, in seconds.
                                          By default, the run uses timeout specified in the default run configuration for the Actor.
            wait_for_finish (int, optional): The maximum number of seconds the server waits for the run to finish.
                                               By default, it is 0, the maximum value is 60.
            webhooks (list of dict, optional): Optional ad-hoc webhooks (https://docs.apify.com/webhooks/ad-hoc-webhooks)
                                               associated with the Actor run which can be used to receive a notification,
                                               e.g. when the Actor finished or failed.
                                               If you already have a webhook set up for the Actor or task, you do not have to add it again here.
                                               Each webhook is represented by a dictionary containing these items:
                                               * ``event_types``: list of ``WebhookEventType`` values which trigger the webhook
                                               * ``request_url``: URL to which to send the webhook HTTP request
                                               * ``payload_template`` (optional): Optional template for the request payload

        Returns:
            dict: The run object
        """
        run_input, content_type = encode_key_value_store_record_value(run_input, content_type)

        request_params = self._params(
            build=build,
            maxItems=max_items,
            memory=memory_mbytes,
            timeout=timeout_secs,
            waitForFinish=wait_for_finish,
            webhooks=encode_webhook_list_to_base64(webhooks) if webhooks is not None else None,
        )

        response = self.http_client.call(
            url=self._url('runs'),
            method='POST',
            headers={'content-type': content_type},
            data=run_input,
            params=request_params,
        )

        return parse_date_fields(pluck_data(response.json()))

    def call(
        self: ActorClient,
        *,
        run_input: Any = None,
        content_type: str | None = None,
        build: str | None = None,
        max_items: int | None = None,
        memory_mbytes: int | None = None,
        timeout_secs: int | None = None,
        webhooks: list[dict] | None = None,
        wait_secs: int | None = None,
    ) -> dict | None:
        """Start the Actor and wait for it to finish before returning the Run object.

        It waits indefinitely, unless the wait_secs argument is provided.

        https://docs.apify.com/api/v2#/reference/actors/run-collection/run-actor

        Args:
            run_input (Any, optional): The input to pass to the Actor run.
            content_type (str, optional): The content type of the input.
            build (str, optional): Specifies the Actor build to run. It can be either a build tag or build number.
                                   By default, the run uses the build specified in the default run configuration for the Actor (typically latest).
            max_items (int, optional): Maximum number of results that will be returned by this run.
                                       If the Actor is charged per result, you will not be charged for more results than the given limit.
            memory_mbytes (int, optional): Memory limit for the run, in megabytes.
                                           By default, the run uses a memory limit specified in the default run configuration for the Actor.
            timeout_secs (int, optional): Optional timeout for the run, in seconds.
                                          By default, the run uses timeout specified in the default run configuration for the Actor.
            webhooks (list, optional): Optional webhooks (https://docs.apify.com/webhooks) associated with the Actor run,
                                       which can be used to receive a notification, e.g. when the Actor finished or failed.
                                       If you already have a webhook set up for the Actor, you do not have to add it again here.
            wait_secs (int, optional): The maximum number of seconds the server waits for the run to finish. If not provided, waits indefinitely.

        Returns:
            dict: The run object
        """
        started_run = self.start(
            run_input=run_input,
            content_type=content_type,
            build=build,
            max_items=max_items,
            memory_mbytes=memory_mbytes,
            timeout_secs=timeout_secs,
            webhooks=webhooks,
        )

        return self.root_client.run(started_run['id']).wait_for_finish(wait_secs=wait_secs)

    def build(
        self: ActorClient,
        *,
        version_number: str,
        beta_packages: bool | None = None,
        tag: str | None = None,
        use_cache: bool | None = None,
        wait_for_finish: int | None = None,
    ) -> dict:
        """Build the Actor.

        https://docs.apify.com/api/v2#/reference/actors/build-collection/build-actor

        Args:
            version_number (str): Actor version number to be built.
            beta_packages (bool, optional): If True, then the Actor is built with beta versions of Apify NPM packages.
                                            By default, the build uses latest stable packages.
            tag (str, optional): Tag to be applied to the build on success. By default, the tag is taken from the Actor version's buildTag property.
            use_cache (bool, optional): If true, the Actor's Docker container will be rebuilt using layer cache
                                        (https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#leverage-build-cache).
                                        This is to enable quick rebuild during development.
                                        By default, the cache is not used.
            wait_for_finish (int, optional): The maximum number of seconds the server waits for the build to finish before returning.
                                             By default it is 0, the maximum value is 60.

        Returns:
            dict: The build object
        """
        request_params = self._params(
            version=version_number,
            betaPackages=beta_packages,
            tag=tag,
            useCache=use_cache,
            waitForFinish=wait_for_finish,
        )

        response = self.http_client.call(
            url=self._url('builds'),
            method='POST',
            params=request_params,
        )

        return parse_date_fields(pluck_data(response.json()))

    def builds(self: ActorClient) -> BuildCollectionClient:
        """Retrieve a client for the builds of this Actor."""
        return BuildCollectionClient(**self._sub_resource_init_options(resource_path='builds'))

    def runs(self: ActorClient) -> RunCollectionClient:
        """Retrieve a client for the runs of this Actor."""
        return RunCollectionClient(**self._sub_resource_init_options(resource_path='runs'))

    def last_run(
        self: ActorClient,
        *,
        status: ActorJobStatus | None = None,
        origin: MetaOrigin | None = None,
    ) -> RunClient:
        """Retrieve the client for the last run of this Actor.

        Last run is retrieved based on the start time of the runs.

        Args:
            status (ActorJobStatus, optional): Consider only runs with this status.
            origin (MetaOrigin, optional): Consider only runs started with this origin.

        Returns:
            RunClient: The resource client for the last run of this Actor.
        """
        return RunClient(
            **self._sub_resource_init_options(
                resource_id='last',
                resource_path='runs',
                params=self._params(
                    status=maybe_extract_enum_member_value(status),
                    origin=maybe_extract_enum_member_value(origin),
                ),
            )
        )

    def versions(self: ActorClient) -> ActorVersionCollectionClient:
        """Retrieve a client for the versions of this Actor."""
        return ActorVersionCollectionClient(**self._sub_resource_init_options())

    def version(self: ActorClient, version_number: str) -> ActorVersionClient:
        """Retrieve the client for the specified version of this Actor.

        Args:
            version_number (str): The version number for which to retrieve the resource client.

        Returns:
            ActorVersionClient: The resource client for the specified Actor version.
        """
        return ActorVersionClient(**self._sub_resource_init_options(resource_id=version_number))

    def webhooks(self: ActorClient) -> WebhookCollectionClient:
        """Retrieve a client for webhooks associated with this Actor."""
        return WebhookCollectionClient(**self._sub_resource_init_options())


class ActorClientAsync(ResourceClientAsync):
    """Async sub-client for manipulating a single Actor."""

    @ignore_docs
    def __init__(self: ActorClientAsync, *args: Any, **kwargs: Any) -> None:
        """Initialize the ActorClientAsync."""
        resource_path = kwargs.pop('resource_path', 'acts')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def get(self: ActorClientAsync) -> dict | None:
        """Retrieve the Actor.

        https://docs.apify.com/api/v2#/reference/actors/actor-object/get-actor

        Returns:
            dict, optional: The retrieved Actor
        """
        return await self._get()

    async def update(
        self: ActorClientAsync,
        *,
        name: str | None = None,
        title: str | None = None,
        description: str | None = None,
        seo_title: str | None = None,
        seo_description: str | None = None,
        versions: list[dict] | None = None,
        restart_on_error: bool | None = None,
        is_public: bool | None = None,
        is_deprecated: bool | None = None,
        is_anonymously_runnable: bool | None = None,
        categories: list[str] | None = None,
        default_run_build: str | None = None,
        default_run_max_items: int | None = None,
        default_run_memory_mbytes: int | None = None,
        default_run_timeout_secs: int | None = None,
        example_run_input_body: Any = None,
        example_run_input_content_type: str | None = None,
        actor_standby_is_enabled: bool | None = None,
        actor_standby_desired_requests_per_actor_run: int | None = None,
        actor_standby_max_requests_per_actor_run: int | None = None,
        actor_standby_idle_timeout_secs: int | None = None,
        actor_standby_build: str | None = None,
        actor_standby_memory_mbytes: int | None = None,
    ) -> dict:
        """Update the Actor with the specified fields.

        https://docs.apify.com/api/v2#/reference/actors/actor-object/update-actor

        Args:
            name (str, optional): The name of the Actor
            title (str, optional): The title of the Actor (human-readable)
            description (str, optional): The description for the Actor
            seo_title (str, optional): The title of the Actor optimized for search engines
            seo_description (str, optional): The description of the Actor optimized for search engines
            versions (list of dict, optional): The list of Actor versions
            restart_on_error (bool, optional): If true, the main Actor run process will be restarted whenever it exits with a non-zero status code.
            is_public (bool, optional): Whether the Actor is public.
            is_deprecated (bool, optional): Whether the Actor is deprecated.
            is_anonymously_runnable (bool, optional): Whether the Actor is anonymously runnable.
            categories (list of str, optional): The categories to which the Actor belongs to.
            default_run_build (str, optional): Tag or number of the build that you want to run by default.
            default_run_max_items (int, optional): Default limit of the number of results that will be returned by runs of this Actor,
                                                   if the Actor is charged per result.
            default_run_memory_mbytes (int, optional): Default amount of memory allocated for the runs of this Actor, in megabytes.
            default_run_timeout_secs (int, optional): Default timeout for the runs of this Actor in seconds.
            example_run_input_body (Any, optional): Input to be prefilled as default input to new users of this Actor.
            example_run_input_content_type (str, optional): The content type of the example run input.
            actor_standby_is_enabled (bool, optional): Whether the Actor Standby is enabled.
            actor_standby_desired_requests_per_actor_run (int, optional): The desired number of concurrent HTTP requests for
                a single Actor Standby run.
            actor_standby_max_requests_per_actor_run (int, optional): The maximum number of concurrent HTTP requests for a single Actor Standby run.
            actor_standby_idle_timeout_secs (int, optional): If the Actor run does not receive any requests for this time, it will be shut down.
            actor_standby_build (str, optional): The build tag or number to run when the Actor is in Standby mode.
            actor_standby_memory_mbytes (int, optional): The memory in megabytes to use when the Actor is in Standby mode.

        Returns:
            dict: The updated Actor
        """
        actor_representation = get_actor_representation(
            name=name,
            title=title,
            description=description,
            seo_title=seo_title,
            seo_description=seo_description,
            versions=versions,
            restart_on_error=restart_on_error,
            is_public=is_public,
            is_deprecated=is_deprecated,
            is_anonymously_runnable=is_anonymously_runnable,
            categories=categories,
            default_run_build=default_run_build,
            default_run_max_items=default_run_max_items,
            default_run_memory_mbytes=default_run_memory_mbytes,
            default_run_timeout_secs=default_run_timeout_secs,
            example_run_input_body=example_run_input_body,
            example_run_input_content_type=example_run_input_content_type,
            actor_standby_is_enabled=actor_standby_is_enabled,
            actor_standby_desired_requests_per_actor_run=actor_standby_desired_requests_per_actor_run,
            actor_standby_max_requests_per_actor_run=actor_standby_max_requests_per_actor_run,
            actor_standby_idle_timeout_secs=actor_standby_idle_timeout_secs,
            actor_standby_build=actor_standby_build,
            actor_standby_memory_mbytes=actor_standby_memory_mbytes,
        )

        return await self._update(filter_out_none_values_recursively(actor_representation))

    async def delete(self: ActorClientAsync) -> None:
        """Delete the Actor.

        https://docs.apify.com/api/v2#/reference/actors/actor-object/delete-actor
        """
        return await self._delete()

    async def start(
        self: ActorClientAsync,
        *,
        run_input: Any = None,
        content_type: str | None = None,
        build: str | None = None,
        max_items: int | None = None,
        memory_mbytes: int | None = None,
        timeout_secs: int | None = None,
        wait_for_finish: int | None = None,
        webhooks: list[dict] | None = None,
    ) -> dict:
        """Start the Actor and immediately return the Run object.

        https://docs.apify.com/api/v2#/reference/actors/run-collection/run-actor

        Args:
            run_input (Any, optional): The input to pass to the Actor run.
            content_type (str, optional): The content type of the input.
            build (str, optional): Specifies the Actor build to run. It can be either a build tag or build number.
                                   By default, the run uses the build specified in the default run configuration for the Actor (typically latest).
            max_items (int, optional): Maximum number of results that will be returned by this run.
                                       If the Actor is charged per result, you will not be charged for more results than the given limit.
            memory_mbytes (int, optional): Memory limit for the run, in megabytes.
                                           By default, the run uses a memory limit specified in the default run configuration for the Actor.
            timeout_secs (int, optional): Optional timeout for the run, in seconds.
                                          By default, the run uses timeout specified in the default run configuration for the Actor.
            wait_for_finish (int, optional): The maximum number of seconds the server waits for the run to finish.
                                               By default, it is 0, the maximum value is 60.
            webhooks (list of dict, optional): Optional ad-hoc webhooks (https://docs.apify.com/webhooks/ad-hoc-webhooks)
                                               associated with the Actor run which can be used to receive a notification,
                                               e.g. when the Actor finished or failed.
                                               If you already have a webhook set up for the Actor or task, you do not have to add it again here.
                                               Each webhook is represented by a dictionary containing these items:
                                               * ``event_types``: list of ``WebhookEventType`` values which trigger the webhook
                                               * ``request_url``: URL to which to send the webhook HTTP request
                                               * ``payload_template`` (optional): Optional template for the request payload

        Returns:
            dict: The run object
        """
        run_input, content_type = encode_key_value_store_record_value(run_input, content_type)

        request_params = self._params(
            build=build,
            maxItems=max_items,
            memory=memory_mbytes,
            timeout=timeout_secs,
            waitForFinish=wait_for_finish,
            webhooks=encode_webhook_list_to_base64(webhooks) if webhooks is not None else None,
        )

        response = await self.http_client.call(
            url=self._url('runs'),
            method='POST',
            headers={'content-type': content_type},
            data=run_input,
            params=request_params,
        )

        return parse_date_fields(pluck_data(response.json()))

    async def call(
        self: ActorClientAsync,
        *,
        run_input: Any = None,
        content_type: str | None = None,
        build: str | None = None,
        max_items: int | None = None,
        memory_mbytes: int | None = None,
        timeout_secs: int | None = None,
        webhooks: list[dict] | None = None,
        wait_secs: int | None = None,
    ) -> dict | None:
        """Start the Actor and wait for it to finish before returning the Run object.

        It waits indefinitely, unless the wait_secs argument is provided.

        https://docs.apify.com/api/v2#/reference/actors/run-collection/run-actor

        Args:
            run_input (Any, optional): The input to pass to the Actor run.
            content_type (str, optional): The content type of the input.
            build (str, optional): Specifies the Actor build to run. It can be either a build tag or build number.
                                   By default, the run uses the build specified in the default run configuration for the Actor (typically latest).
            max_items (int, optional): Maximum number of results that will be returned by this run.
                                       If the Actor is charged per result, you will not be charged for more results than the given limit.
            memory_mbytes (int, optional): Memory limit for the run, in megabytes.
                                           By default, the run uses a memory limit specified in the default run configuration for the Actor.
            timeout_secs (int, optional): Optional timeout for the run, in seconds.
                                          By default, the run uses timeout specified in the default run configuration for the Actor.
            webhooks (list, optional): Optional webhooks (https://docs.apify.com/webhooks) associated with the Actor run,
                                       which can be used to receive a notification, e.g. when the Actor finished or failed.
                                       If you already have a webhook set up for the Actor, you do not have to add it again here.
            wait_secs (int, optional): The maximum number of seconds the server waits for the run to finish. If not provided, waits indefinitely.

        Returns:
            dict: The run object
        """
        started_run = await self.start(
            run_input=run_input,
            content_type=content_type,
            build=build,
            max_items=max_items,
            memory_mbytes=memory_mbytes,
            timeout_secs=timeout_secs,
            webhooks=webhooks,
        )

        return await self.root_client.run(started_run['id']).wait_for_finish(wait_secs=wait_secs)

    async def build(
        self: ActorClientAsync,
        *,
        version_number: str,
        beta_packages: bool | None = None,
        tag: str | None = None,
        use_cache: bool | None = None,
        wait_for_finish: int | None = None,
    ) -> dict:
        """Build the Actor.

        https://docs.apify.com/api/v2#/reference/actors/build-collection/build-actor

        Args:
            version_number (str): Actor version number to be built.
            beta_packages (bool, optional): If True, then the Actor is built with beta versions of Apify NPM packages.
                                            By default, the build uses latest stable packages.
            tag (str, optional): Tag to be applied to the build on success. By default, the tag is taken from the Actor version's buildTag property.
            use_cache (bool, optional): If true, the Actor's Docker container will be rebuilt using layer cache
                                        (https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#leverage-build-cache).
                                        This is to enable quick rebuild during development.
                                        By default, the cache is not used.
            wait_for_finish (int, optional): The maximum number of seconds the server waits for the build to finish before returning.
                                             By default it is 0, the maximum value is 60.

        Returns:
            dict: The build object
        """
        request_params = self._params(
            version=version_number,
            betaPackages=beta_packages,
            tag=tag,
            useCache=use_cache,
            waitForFinish=wait_for_finish,
        )

        response = await self.http_client.call(
            url=self._url('builds'),
            method='POST',
            params=request_params,
        )

        return parse_date_fields(pluck_data(response.json()))

    def builds(self: ActorClientAsync) -> BuildCollectionClientAsync:
        """Retrieve a client for the builds of this Actor."""
        return BuildCollectionClientAsync(**self._sub_resource_init_options(resource_path='builds'))

    def runs(self: ActorClientAsync) -> RunCollectionClientAsync:
        """Retrieve a client for the runs of this Actor."""
        return RunCollectionClientAsync(**self._sub_resource_init_options(resource_path='runs'))

    def last_run(self: ActorClientAsync, *, status: ActorJobStatus | None = None, origin: MetaOrigin | None = None) -> RunClientAsync:
        """Retrieve the client for the last run of this Actor.

        Last run is retrieved based on the start time of the runs.

        Args:
            status (ActorJobStatus, optional): Consider only runs with this status.
            origin (MetaOrigin, optional): Consider only runs started with this origin.

        Returns:
            RunClientAsync: The resource client for the last run of this Actor.
        """
        return RunClientAsync(
            **self._sub_resource_init_options(
                resource_id='last',
                resource_path='runs',
                params=self._params(
                    status=maybe_extract_enum_member_value(status),
                    origin=maybe_extract_enum_member_value(origin),
                ),
            )
        )

    def versions(self: ActorClientAsync) -> ActorVersionCollectionClientAsync:
        """Retrieve a client for the versions of this Actor."""
        return ActorVersionCollectionClientAsync(**self._sub_resource_init_options())

    def version(self: ActorClientAsync, version_number: str) -> ActorVersionClientAsync:
        """Retrieve the client for the specified version of this Actor.

        Args:
            version_number (str): The version number for which to retrieve the resource client.

        Returns:
            ActorVersionClientAsync: The resource client for the specified Actor version.
        """
        return ActorVersionClientAsync(**self._sub_resource_init_options(resource_id=version_number))

    def webhooks(self: ActorClientAsync) -> WebhookCollectionClientAsync:
        """Retrieve a client for webhooks associated with this Actor."""
        return WebhookCollectionClientAsync(**self._sub_resource_init_options())
