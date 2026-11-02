from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

from apify_client._docs import docs_group
from apify_client._models import ActorResponse
from apify_client._resource_clients._resource_client import ResourceClient, ResourceClientAsync
from apify_client._utils.http import response_to_dict
from apify_client.errors import ApifyClientError
from apify_client.http_compressors._resolve import resolve_compressor

if TYPE_CHECKING:
    from apify_client._literals import HttpMethod
    from apify_client.http_clients import HttpResponse
    from apify_client.http_compressors import HttpCompressor
    from apify_client.types import HttpCompressionAlgorithm, JsonSerializable, QueryParams, Timeout


SERVER_RETRY_STATUS_CODES = frozenset({429, 503})
"""Statuses a server request is retried on. The platform answers with them when it can't pass a request to a server run,
so a retry usually doesn't run the Actor's code again. An Actor that returns one itself gets the request again."""

_BUILD_NUMBER_PATTERN = re.compile(r'(\d+)\.(\d+)\.(\d+)')


def _parse_build_number(build_number: str | None) -> tuple[int, int, int] | None:
    """Split a build number like `0.1.23` into its version and sequence number, or return `None` for anything else."""
    match = _BUILD_NUMBER_PATTERN.fullmatch(build_number or '')
    if match is None:
        return None
    major, minor, sequence = match.groups()
    return int(major), int(minor), int(sequence)


def _is_older_build(build_number: str | None, target: tuple[int, int, int]) -> bool:
    """Return whether `build_number` belongs to the same version as `target` and comes before it.

    Builds are listed newest first and the sequence numbers of a version grow over time, so meeting such a build means
    the target build doesn't exist.
    """
    parsed = _parse_build_number(build_number)
    return parsed is not None and parsed[:2] == target[:2] and parsed < target


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

    def get_url(self, *, timeout: Timeout = 'short') -> str:
        """Return the URL of the Actor's server.

        The URL is the Actor's `standby_url`, fetched from the API by the first call of this method or
        `get_openapi_spec` and reused by later calls on this client. Use it to call the server with another HTTP client,
        for example one generated from the server's OpenAPI specification.

        https://docs.apify.com/platform/actors/running/standby

        Args:
            timeout: Timeout for the API HTTP request.

        Returns:
            The URL of the Actor's server.

        Raises:
            ApifyClientError: If the Actor is not a Server Actor.
            ApifyApiError: If the Actor does not exist.
        """
        if self._url is None:
            response = self._http_client.call(url=self._build_url(), method='GET', timeout=timeout)
            actor = ActorResponse.model_validate(response_to_dict(response)).data
            if actor.standby_url is None:
                raise ApifyClientError(f'Actor {self.resource_id} is not a Server Actor.')
            self._url = actor.standby_url
        return self._url

    def get_openapi_spec(self, *, timeout: Timeout = 'short') -> dict[str, Any] | None:
        """Return the OpenAPI specification of the Actor's server.

        The specification is the web server schema from the Actor's definition, taken from the build that serves the
        server interface: the build set in `actor_standby.build`, or `latest` if none is set. Use it to generate an HTTP
        client for the server, and point that client at the URL returned by `get_url`.

        https://docs.apify.com/platform/actors/development/actor-definition/web-server-schema

        Args:
            timeout: Timeout for each API HTTP request.

        Returns:
            The OpenAPI specification of the Actor's server, or `None` if the Actor's definition doesn't include one.

        Raises:
            ApifyClientError: If the Actor is not a Server Actor, or the build that serves its server interface doesn't
                exist.
            ApifyApiError: If the Actor does not exist.
        """
        response = self._http_client.call(url=self._build_url(), method='GET', timeout=timeout)
        actor = ActorResponse.model_validate(response_to_dict(response)).data
        if actor.standby_url is None:
            raise ApifyClientError(f'Actor {self.resource_id} is not a Server Actor.')
        self._url = actor.standby_url

        build_ref = (actor.actor_standby.build if actor.actor_standby else None) or 'latest'

        build_id = None
        tagged_build = (actor.tagged_builds or {}).get(build_ref)
        target_build_number = _parse_build_number(build_ref)
        if tagged_build is not None:
            build_id = tagged_build.build_id
        elif target_build_number is not None:
            # Not a tag, so look `build_ref` up as a build number, which the API can't resolve directly.
            builds_client = self._client_registry.build_collection_client(
                resource_path='builds',
                **self._base_client_kwargs,
            )
            for build_item in builds_client.iterate(desc=True, timeout=timeout):
                if build_item.build_number == build_ref:
                    build_id = build_item.id
                    break
                if _is_older_build(build_item.build_number, target_build_number):
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
            build = build_client.get(timeout=timeout)
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
        params: QueryParams | None = None,
        headers: dict[str, str] | None = None,
        data: str | bytes | None = None,
        json: JsonSerializable | None = None,
        compression: HttpCompressionAlgorithm | HttpCompressor | None = None,
        stream: bool = False,
        timeout: Timeout = 'long',
    ) -> HttpResponse:
        """Send an HTTP request to the Actor's server.

        The request goes to the URL returned by `get_url` and carries the client's token in the `X-Apify-Authorization`
        header, which the platform consumes, so it never reaches the Actor's code. Headers you pass, `Authorization`
        included, reach the Actor's server as they are. The first request to an idle Actor waits for the platform to
        start a server run, which is why the timeout defaults to `long`.

        The method returns any response of the server, error statuses included. A rate-limit (429) or Service
        Unavailable (503) response is retried with the client's retry settings, and the last one is returned once the
        retries run out. The Actor's code can return these statuses too, and then it gets the request again. A redirect
        is returned as it is, since following it would send the token to a host the Actor's code picked. Request
        bodies are sent uncompressed unless `compression` is set, since the Actor's server may not decode a compressed
        body.

        https://docs.apify.com/platform/actors/running/standby

        Args:
            path: The path on the Actor's server, for example `/search`. It is always resolved against the server URL,
                so the request, and the token with it, cannot be sent to another host. Pass the query in `params`. A
                fragment (`#...`) is dropped, since it is never sent to the server.
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
            stream: Whether to return the response with the body unread, so it can be read in chunks with `iter_bytes`
                (`aiter_bytes` in the async client). The response holds its connection open until you close it.
            timeout: Timeout for the HTTP request. With `stream`, it bounds the wait for the server to start responding.

        Returns:
            The response of the Actor's server.

        Raises:
            ApifyClientError: If the Actor is not a Server Actor.
            ApifyApiError: If the Actor does not exist.
            ImportError: If `compression` needs an optional extra that is not installed.
            ValueError: If both `data` and `json` are passed, or `compression` is not a supported algorithm.
        """
        server_url = self.get_url()
        server_path = path.partition('#')[0].lstrip('/')
        return self._http_client.call(
            url=f'{server_url.rstrip("/")}/{server_path}',
            method=method,
            params=params,
            headers=headers,
            data=data,
            json=json,
            timeout=timeout,
            compression=resolve_compressor(compression) if compression is not None else False,
            authorization_header='X-Apify-Authorization',
            raise_for_status=False,
            retry_status_codes=SERVER_RETRY_STATUS_CODES,
            retry_transport_errors=False,
            follow_redirects=False,
            stream=stream,
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

    async def get_url(self, *, timeout: Timeout = 'short') -> str:
        """Return the URL of the Actor's server.

        The URL is the Actor's `standby_url`, fetched from the API by the first call of this method or
        `get_openapi_spec` and reused by later calls on this client. Use it to call the server with another HTTP client,
        for example one generated from the server's OpenAPI specification.

        https://docs.apify.com/platform/actors/running/standby

        Args:
            timeout: Timeout for the API HTTP request.

        Returns:
            The URL of the Actor's server.

        Raises:
            ApifyClientError: If the Actor is not a Server Actor.
            ApifyApiError: If the Actor does not exist.
        """
        if self._url is None:
            response = await self._http_client.call(url=self._build_url(), method='GET', timeout=timeout)
            actor = ActorResponse.model_validate(response_to_dict(response)).data
            if actor.standby_url is None:
                raise ApifyClientError(f'Actor {self.resource_id} is not a Server Actor.')
            self._url = actor.standby_url
        return self._url

    async def get_openapi_spec(self, *, timeout: Timeout = 'short') -> dict[str, Any] | None:
        """Return the OpenAPI specification of the Actor's server.

        The specification is the web server schema from the Actor's definition, taken from the build that serves the
        server interface: the build set in `actor_standby.build`, or `latest` if none is set. Use it to generate an HTTP
        client for the server, and point that client at the URL returned by `get_url`.

        https://docs.apify.com/platform/actors/development/actor-definition/web-server-schema

        Args:
            timeout: Timeout for each API HTTP request.

        Returns:
            The OpenAPI specification of the Actor's server, or `None` if the Actor's definition doesn't include one.

        Raises:
            ApifyClientError: If the Actor is not a Server Actor, or the build that serves its server interface doesn't
                exist.
            ApifyApiError: If the Actor does not exist.
        """
        response = await self._http_client.call(url=self._build_url(), method='GET', timeout=timeout)
        actor = ActorResponse.model_validate(response_to_dict(response)).data
        if actor.standby_url is None:
            raise ApifyClientError(f'Actor {self.resource_id} is not a Server Actor.')
        self._url = actor.standby_url

        build_ref = (actor.actor_standby.build if actor.actor_standby else None) or 'latest'

        build_id = None
        tagged_build = (actor.tagged_builds or {}).get(build_ref)
        target_build_number = _parse_build_number(build_ref)
        if tagged_build is not None:
            build_id = tagged_build.build_id
        elif target_build_number is not None:
            # Not a tag, so look `build_ref` up as a build number, which the API can't resolve directly.
            builds_client = self._client_registry.build_collection_client(
                resource_path='builds',
                **self._base_client_kwargs,
            )
            async for build_item in builds_client.iterate(desc=True, timeout=timeout):
                if build_item.build_number == build_ref:
                    build_id = build_item.id
                    break
                if _is_older_build(build_item.build_number, target_build_number):
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
            build = await build_client.get(timeout=timeout)
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
        params: QueryParams | None = None,
        headers: dict[str, str] | None = None,
        data: str | bytes | None = None,
        json: JsonSerializable | None = None,
        compression: HttpCompressionAlgorithm | HttpCompressor | None = None,
        stream: bool = False,
        timeout: Timeout = 'long',
    ) -> HttpResponse:
        """Send an HTTP request to the Actor's server.

        The request goes to the URL returned by `get_url` and carries the client's token in the `X-Apify-Authorization`
        header, which the platform consumes, so it never reaches the Actor's code. Headers you pass, `Authorization`
        included, reach the Actor's server as they are. The first request to an idle Actor waits for the platform to
        start a server run, which is why the timeout defaults to `long`.

        The method returns any response of the server, error statuses included. A rate-limit (429) or Service
        Unavailable (503) response is retried with the client's retry settings, and the last one is returned once the
        retries run out. The Actor's code can return these statuses too, and then it gets the request again. A redirect
        is returned as it is, since following it would send the token to a host the Actor's code picked. Request
        bodies are sent uncompressed unless `compression` is set, since the Actor's server may not decode a compressed
        body.

        https://docs.apify.com/platform/actors/running/standby

        Args:
            path: The path on the Actor's server, for example `/search`. It is always resolved against the server URL,
                so the request, and the token with it, cannot be sent to another host. Pass the query in `params`. A
                fragment (`#...`) is dropped, since it is never sent to the server.
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
            stream: Whether to return the response with the body unread, so it can be read in chunks with `iter_bytes`
                (`aiter_bytes` in the async client). The response holds its connection open until you close it.
            timeout: Timeout for the HTTP request. With `stream`, it bounds the wait for the server to start responding.

        Returns:
            The response of the Actor's server.

        Raises:
            ApifyClientError: If the Actor is not a Server Actor.
            ApifyApiError: If the Actor does not exist.
            ImportError: If `compression` needs an optional extra that is not installed.
            ValueError: If both `data` and `json` are passed, or `compression` is not a supported algorithm.
        """
        server_url = await self.get_url()
        server_path = path.partition('#')[0].lstrip('/')
        return await self._http_client.call(
            url=f'{server_url.rstrip("/")}/{server_path}',
            method=method,
            params=params,
            headers=headers,
            data=data,
            json=json,
            timeout=timeout,
            compression=resolve_compressor(compression) if compression is not None else False,
            authorization_header='X-Apify-Authorization',
            raise_for_status=False,
            retry_status_codes=SERVER_RETRY_STATUS_CODES,
            retry_transport_errors=False,
            follow_redirects=False,
            stream=stream,
        )
