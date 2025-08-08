import secrets
import string


def random_string(length: int = 10) -> str:
    return ''.join(secrets.choice(string.ascii_letters) for _ in range(length))


def random_resource_name(resource: str) -> str:
    return f'python-client-test-{resource}-{random_string(5)}'
