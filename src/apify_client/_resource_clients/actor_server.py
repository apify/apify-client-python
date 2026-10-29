from __future__ import annotations

from typing import TYPE_CHECKING, Any

from apify_client._docs import docs_group
from apify_client._models import ActorResponse
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync
from apify_client._utils.http import response_to_dict
from apify_client.errors import ApifyClientError
from apify_client.http_compressors._resolve import resolve_compressor

if TYPE_CHECKING:
    from collections.abc import Mapping
    from datetime import datetime

    from apify_client._literals import HttpMethod
    from apify_client.http_clients import HttpResponse
    from apify_client.http_compressors import HttpCompressor
    from apify_client.types import HttpCompressionAlgorithm, JsonSerializable, Timeout


@docs_group('Resource clients')
class ActorServerClient(ResourceClient):
    """Sub-client for the server interface of a specific Actor.

    Provides methods to work with the web server of a Server Actor, e.g. send it requests or get its OpenAPI
    specification. Obtain an instance via an appropriate method on the `ActorClient` class.
    """

    def __init__(
        self,
        *,
        resource_id: str,
        resource_path: str = 'actors',
        **kwargs: Any,
    ) -> None:
        super().__init__(
            resource_id=resource_id,
            resource_path=resource_path,
            **kwargs,
        )
        self._url: str | None = None

    def get_url(self) -> str:
        """Return the URL of the Actor's server.

        The URL is the Actor's `standby_url`, fetched from the API on the first call and reused by later calls on this
        client. Use it to call the server with another HTTP client, for example one generated from the server's
        OpenAPI specification.

        https://docs.apify.com/platform/actors/running/standby

        Returns:
            The URL of the Actor's server.

        Raises:
            ApifyClientError: If the Actor is not a Server Actor.
            ApifyApiError: If the Actor does not exist.
        """
        if self._url is None:
            response = self._http_client.call(url=self._build_url(), method='GET', timeout='short')
            actor = ActorResponse.model_validate(response_to_dict(response)).data
            if actor.standby_url is None:
                raise ApifyClientError(f'Actor {self.resource_id} is not a Server Actor.')
            self._url = actor.standby_url
        return self._url

    def get_openapi_spec(self) -> dict[str, Any] | None:
        """Return the OpenAPI specification of the Actor's server.

        The specification is the web server schema from the Actor's definition, taken from the build that serves the
        server interface: the build set in `actor_standby.build`, or `latest` if none is set. Use it to generate an HTTP
        client for the server, and point that client at the URL returned by `get_url`.

        https://docs.apify.com/platform/actors/development/actor-definition/web-server-schema

        Returns:
            The OpenAPI specification of the Actor's server, or `None` if the Actor's definition doesn't include one.

        Raises:
            ApifyClientError: If the Actor is not a Server Actor, or the build that serves its server interface doesn't
                exist.
            ApifyApiError: If the Actor does not exist.
        """
        response = self._http_client.call(url=self._build_url(), method='GET', timeout='short')
        actor = ActorResponse.model_validate(response_to_dict(response)).data
        if actor.standby_url is None:
            raise ApifyClientError(f'Actor {self.resource_id} is not a Server Actor.')

        build_ref = (actor.actor_standby.build if actor.actor_standby else None) or 'latest'

        build_id = None
        tagged_build = (actor.tagged_builds or {}).get(build_ref)
        if tagged_build is not None:
            build_id = tagged_build.build_id
        else:
            # Not a tag, so look `build_ref` up as a build number, which the API can't resolve directly.
            builds_client = self._client_registry.build_collection_client(
                resource_path='builds',
                **self._base_client_kwargs,
            )
            for build_item in builds_client.iterate(desc=True):
                if build_item.build_number == build_ref:
                    build_id = build_item.id
                    break

        build = None
        if build_id is not None:
            build_client = self._client_registry.build_client(
                resource_id=build_id,
                base_url=self._base_url,
                public_base_url=self._public_base_url,
                http_client=self._http_client,
                client_registry=self._client_registry,
            )
            build = build_client.get()
        if build is None:
            raise ApifyClientError(f'Build {build_ref} of Actor {self.resource_id} does not exist.')

        if build.actor_definition is None:
            return None
        return build.actor_definition.web_server_schema

    def request(
        self,
        path: str = '/',
        *,
        method: HttpMethod = 'GET',
        params: Mapping[str, str | int | float | bool | datetime | list[str] | None] | None = None,
        headers: dict[str, str] | None = None,
        data: str | bytes | None = None,
        json: JsonSerializable | None = None,
        compression: HttpCompressionAlgorithm | HttpCompressor | None = None,
        timeout: Timeout = 'long',
    ) -> HttpResponse:
        """Send an HTTP request to the Actor's server.

        The request goes to the URL returned by `get_url` and carries the client's token, which the platform consumes,
        so it never reaches the Actor's code. The first request to an idle Actor waits for the platform to start a
        server run, which is why the timeout defaults to `long`.

        A server error or a rate-limit response is retried like an API call, so the server may receive the same
        request more than once. Request bodies are sent uncompressed unless `compression` is set, since the Actor's
        server may not decode a compressed body.

        https://docs.apify.com/platform/actors/running/standby

        Args:
            path: The path on the Actor's server, for example `/search`. It is always resolved against the server URL,
                so the request, and the token with it, cannot be sent to another host. Pass the query in `params`.
            method: HTTP method of the request.
            params: Query parameters of the request, converted the same way as for API calls: booleans become `true`
                or `false`, a list of strings becomes one comma-separated value, a datetime becomes an ISO 8601 string
                in UTC, and `None` values are left out.
            headers: Additional headers of the request.
            data: Raw request body. Cannot be used together with `json`.
            json: JSON-serializable request body. Cannot be used together with `data`.
            compression: Compression algorithm for the request body, as a string literal or an `HttpCompressor`
                instance. The body is compressed under the same conditions as for API calls. Set it only if the
                Actor's server decodes the resulting `Content-Encoding`.
            timeout: Timeout for the HTTP request.

        Returns:
            The response of the Actor's server.

        Raises:
            ApifyClientError: If the Actor is not a Server Actor.
            ApifyApiError: If the Actor does not exist, or the server responds with an error status.
            ImportError: If `compression` needs an optional extra that is not installed.
            ValueError: If both `data` and `json` are passed, or `compression` is not a supported algorithm.
        """
        server_url = self.get_url()
        return self._http_client.call(
            url=f'{server_url.rstrip("/")}/{path.lstrip("/")}',
            method=method,
            params=dict(params) if params is not None else None,
            headers=headers,
            data=data,
            json=json,
            timeout=timeout,
            compression=resolve_compressor(compression) if compression is not None else False,
        )


@docs_group('Resource clients')
class ActorServerClientAsync(ResourceClientAsync):
    """Sub-client for the server interface of a specific Actor.

    Provides methods to work with the web server of a Server Actor, e.g. send it requests or get its OpenAPI
    specification. Obtain an instance via an appropriate method on the `ActorClientAsync` class.
    """

    def __init__(
        self,
        *,
        resource_id: str,
        resource_path: str = 'actors',
        **kwargs: Any,
    ) -> None:
        super().__init__(
            resource_id=resource_id,
            resource_path=resource_path,
            **kwargs,
        )
        self._url: str | None = None

    async def get_url(self) -> str:
        """Return the URL of the Actor's server.

        The URL is the Actor's `standby_url`, fetched from the API on the first call and reused by later calls on this
        client. Use it to call the server with another HTTP client, for example one generated from the server's
        OpenAPI specification.

        https://docs.apify.com/platform/actors/running/standby

        Returns:
            The URL of the Actor's server.

        Raises:
            ApifyClientError: If the Actor is not a Server Actor.
            ApifyApiError: If the Actor does not exist.
        """
        if self._url is None:
            response = await self._http_client.call(url=self._build_url(), method='GET', timeout='short')
            actor = ActorResponse.model_validate(response_to_dict(response)).data
            if actor.standby_url is None:
                raise ApifyClientError(f'Actor {self.resource_id} is not a Server Actor.')
            self._url = actor.standby_url
        return self._url

    async def get_openapi_spec(self) -> dict[str, Any] | None:
        """Return the OpenAPI specification of the Actor's server.

        The specification is the web server schema from the Actor's definition, taken from the build that serves the
        server interface: the build set in `actor_standby.build`, or `latest` if none is set. Use it to generate an HTTP
        client for the server, and point that client at the URL returned by `get_url`.

        https://docs.apify.com/platform/actors/development/actor-definition/web-server-schema

        Returns:
            The OpenAPI specification of the Actor's server, or `None` if the Actor's definition doesn't include one.

        Raises:
            ApifyClientError: If the Actor is not a Server Actor, or the build that serves its server interface doesn't
                exist.
            ApifyApiError: If the Actor does not exist.
        """
        response = await self._http_client.call(url=self._build_url(), method='GET', timeout='short')
        actor = ActorResponse.model_validate(response_to_dict(response)).data
        if actor.standby_url is None:
            raise ApifyClientError(f'Actor {self.resource_id} is not a Server Actor.')

        build_ref = (actor.actor_standby.build if actor.actor_standby else None) or 'latest'

        build_id = None
        tagged_build = (actor.tagged_builds or {}).get(build_ref)
        if tagged_build is not None:
            build_id = tagged_build.build_id
        else:
            # Not a tag, so look `build_ref` up as a build number, which the API can't resolve directly.
            builds_client = self._client_registry.build_collection_client(
                resource_path='builds',
                **self._base_client_kwargs,
            )
            async for build_item in builds_client.iterate(desc=True):
                if build_item.build_number == build_ref:
                    build_id = build_item.id
                    break

        build = None
        if build_id is not None:
            build_client = self._client_registry.build_client(
                resource_id=build_id,
                base_url=self._base_url,
                public_base_url=self._public_base_url,
                http_client=self._http_client,
                client_registry=self._client_registry,
            )
            build = await build_client.get()
        if build is None:
            raise ApifyClientError(f'Build {build_ref} of Actor {self.resource_id} does not exist.')

        if build.actor_definition is None:
            return None
        return build.actor_definition.web_server_schema

    async def request(
        self,
        path: str = '/',
        *,
        method: HttpMethod = 'GET',
        params: Mapping[str, str | int | float | bool | datetime | list[str] | None] | None = None,
        headers: dict[str, str] | None = None,
        data: str | bytes | None = None,
        json: JsonSerializable | None = None,
        compression: HttpCompressionAlgorithm | HttpCompressor | None = None,
        timeout: Timeout = 'long',
    ) -> HttpResponse:
        """Send an HTTP request to the Actor's server.

        The request goes to the URL returned by `get_url` and carries the client's token, which the platform consumes,
        so it never reaches the Actor's code. The first request to an idle Actor waits for the platform to start a
        server run, which is why the timeout defaults to `long`.

        A server error or a rate-limit response is retried like an API call, so the server may receive the same
        request more than once. Request bodies are sent uncompressed unless `compression` is set, since the Actor's
        server may not decode a compressed body.

        https://docs.apify.com/platform/actors/running/standby

        Args:
            path: The path on the Actor's server, for example `/search`. It is always resolved against the server URL,
                so the request, and the token with it, cannot be sent to another host. Pass the query in `params`.
            method: HTTP method of the request.
            params: Query parameters of the request, converted the same way as for API calls: booleans become `true`
                or `false`, a list of strings becomes one comma-separated value, a datetime becomes an ISO 8601 string
                in UTC, and `None` values are left out.
            headers: Additional headers of the request.
            data: Raw request body. Cannot be used together with `json`.
            json: JSON-serializable request body. Cannot be used together with `data`.
            compression: Compression algorithm for the request body, as a string literal or an `HttpCompressor`
                instance. The body is compressed under the same conditions as for API calls. Set it only if the
                Actor's server decodes the resulting `Content-Encoding`.
            timeout: Timeout for the HTTP request.

        Returns:
            The response of the Actor's server.

        Raises:
            ApifyClientError: If the Actor is not a Server Actor.
            ApifyApiError: If the Actor does not exist, or the server responds with an error status.
            ImportError: If `compression` needs an optional extra that is not installed.
            ValueError: If both `data` and `json` are passed, or `compression` is not a supported algorithm.
        """
        server_url = await self.get_url()
        return await self._http_client.call(
            url=f'{server_url.rstrip("/")}/{path.lstrip("/")}',
            method=method,
            params=dict(params) if params is not None else None,
            headers=headers,
            data=data,
            json=json,
            timeout=timeout,
            compression=resolve_compressor(compression) if compression is not None else False,
        )
