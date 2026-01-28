import dataclasses
import secrets
import string
from typing import Any

import pytest


@dataclasses.dataclass
class StorageFixture:
    """Storage resource fixture with ID and signature."""

    id: str
    signature: str


@dataclasses.dataclass
class DatasetFixture(StorageFixture):
    """Dataset fixture with expected content."""

    expected_content: list


@dataclasses.dataclass
class KvsFixture(StorageFixture):
    """Key-value store fixture with expected content and key signatures."""

    expected_content: dict[str, Any]
    keys_signature: dict[str, str]


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


# Parametrize decorator for testing various API URL and public URL combinations
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
