from __future__ import annotations

import asyncio
import secrets
import string
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, TypeVar, overload

import pytest

if TYPE_CHECKING:
    from collections.abc import Coroutine

# Environment variable names for test configuration
TOKEN_ENV_VAR = 'APIFY_TEST_USER_API_TOKEN'
TOKEN_ENV_VAR_2 = 'APIFY_TEST_USER_2_API_TOKEN'
API_URL_ENV_VAR = 'APIFY_INTEGRATION_TESTS_API_URL'

T = TypeVar('T')


# ============================================================================
# Data classes for test fixtures
# ============================================================================


@dataclass
class StorageFixture:
    """Base storage fixture with ID and signature."""

    id: str
    signature: str


@dataclass
class DatasetFixture(StorageFixture):
    """Dataset fixture with expected content."""

    expected_content: list


@dataclass
class KvsFixture(StorageFixture):
    """Key-value store fixture with expected content and key signatures."""

    expected_content: dict[str, Any]
    keys_signature: dict[str, str]


# ============================================================================
# Helper functions
# ============================================================================


def get_crypto_random_object_id(length: int = 17) -> str:
    """Generate a cryptographically secure random object ID."""
    chars = 'abcdefghijklmnopqrstuvwxyzABCEDFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join(secrets.choice(chars) for _ in range(length))


def get_random_string(length: int = 10) -> str:
    """Generate a random alphabetic string."""
    return ''.join(secrets.choice(string.ascii_letters) for _ in range(length))


def get_random_resource_name(resource: str) -> str:
    """Generate a random resource name for test resources."""
    return f'python-client-test-{resource}-{get_random_string(5)}'


@overload
async def maybe_await(value: Coroutine[Any, Any, T]) -> T: ...


@overload
async def maybe_await(value: T) -> T: ...


async def maybe_await(value: T | Coroutine[Any, Any, T]) -> T:
    """Await coroutines, pass through other values.

    Enables unified test code for both sync and async clients:
        result = await maybe_await(client.datasets().list())
    """
    if hasattr(value, '__await__'):
        return await value  # ty: ignore[invalid-await]
    return value


async def maybe_sleep(seconds: float, *, is_async: bool) -> None:
    """Sleep using asyncio or time.sleep based on client type."""
    if is_async:
        await asyncio.sleep(seconds)
    else:
        time.sleep(seconds)  # noqa: ASYNC251


# ============================================================================
# Pytest markers and parametrization
# ============================================================================

parametrized_api_urls = pytest.mark.parametrize(
    ('api_url', 'api_public_url'),
    [
        ('https://api.apify.com', 'https://api.apify.com'),
        ('https://api.apify.com', None),
        ('https://api.apify.com', 'https://custom-public-url.com'),
        ('https://api.apify.com', 'https://custom-public-url.com/with/custom/path'),
        ('https://api.apify.com', 'https://custom-public-url.com/with/custom/path/'),
        ('http://10.0.88.214:8010', 'https://api.apify.com'),
        ('http://10.0.88.214:8010', None),
    ],
)
"""Parametrize decorator for testing various API URL and public URL combinations."""
