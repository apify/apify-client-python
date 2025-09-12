import secrets
import string

import pytest


def random_string(length: int = 10) -> str:
    return ''.join(secrets.choice(string.ascii_letters) for _ in range(length))


def random_resource_name(resource: str) -> str:
    return f'python-client-test-{resource}-{random_string(5)}'


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
