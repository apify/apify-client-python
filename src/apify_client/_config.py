from __future__ import annotations

from dataclasses import dataclass

DEFAULT_API_URL = 'https://api.apify.com'
DEFAULT_TIMEOUT = 360
API_VERSION = 'v2'


@dataclass(frozen=True)
class ClientConfig:
    """Immutable configuration for Apify HTTP client.

    This dataclass holds all configuration options needed by the HTTP client
    to communicate with the Apify API. It is created once by ApifyClient
    and shared across all resource clients.

    All fields are frozen (immutable) to prevent accidental modification
    after initialization.
    """

    base_url: str
    """Base URL of the Apify API (e.g., 'https://api.apify.com/v2')."""

    public_base_url: str
    """Public base URL for CDN access (e.g., 'https://cdn.apify.com/v2')."""

    token: str | None = None
    """Apify API token for authentication."""

    max_retries: int = 8
    """Maximum number of retries for failed requests."""

    min_delay_between_retries_millis: int = 500
    """Minimum delay between retries in milliseconds (increases exponentially)."""

    timeout_secs: int = 360
    """Request timeout in seconds."""

    @classmethod
    def from_user_params(
        cls,
        *,
        token: str | None = None,
        api_url: str | None = None,
        api_public_url: str | None = None,
        max_retries: int | None = 8,
        min_delay_between_retries_millis: int | None = 500,
        timeout_secs: int | None = 360,
    ) -> ClientConfig:
        """Create ClientConfig from user-provided parameters.

        This factory method processes user input and creates a properly
        formatted ClientConfig instance with sensible defaults.

        Args:
            token: Apify API token for authentication.
            api_url: Base API URL (default: https://api.apify.com).
            api_public_url: Public CDN URL (default: same as api_url).
            max_retries: Maximum number of retries for failed requests (default: 8).
            min_delay_between_retries_millis: Minimum delay between retries in ms (default: 500).
            timeout_secs: Request timeout in seconds (default: 360).

        Returns:
            Immutable ClientConfig instance.
        """
        api_url = (api_url or DEFAULT_API_URL).rstrip('/')
        api_public_url = (api_public_url or DEFAULT_API_URL).rstrip('/')

        return cls(
            base_url=f'{api_url}/{API_VERSION}',
            public_base_url=f'{api_public_url}/{API_VERSION}',
            token=token,
            max_retries=max_retries or 8,
            min_delay_between_retries_millis=min_delay_between_retries_millis or 500,
            timeout_secs=timeout_secs or DEFAULT_TIMEOUT,
        )
