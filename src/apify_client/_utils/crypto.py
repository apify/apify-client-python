from __future__ import annotations

import hashlib
import hmac
import string
import time
from base64 import urlsafe_b64encode
from typing import TYPE_CHECKING

from apify_client._utils.time import to_seconds

if TYPE_CHECKING:
    from datetime import timedelta

_BASE62_CHARSET = string.digits + string.ascii_letters


def encode_base62(num: int) -> str:
    """Encode an integer to a base62 string.

    Args:
        num: The number to encode.

    Returns:
        The base62-encoded string.
    """
    if num == 0:
        return _BASE62_CHARSET[0]

    # Use list to build result for O(n) complexity instead of O(n^2) string concatenation.
    parts = []
    while num > 0:
        num, remainder = divmod(num, 62)
        parts.append(_BASE62_CHARSET[remainder])

    # Reverse and join once at the end.
    return ''.join(reversed(parts))


def create_hmac_signature(secret_key: str, message: str) -> str:
    """Generate an HMAC-SHA256 signature and encode it using base62.

    The HMAC signature is truncated to 30 characters and then encoded in base62 to reduce the signature length.

    Args:
        secret_key: The secret key used for signing.
        message: The message to be signed.

    Returns:
        The base62-encoded signature.
    """
    signature = hmac.new(secret_key.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).hexdigest()[:30]

    decimal_signature = int(signature, 16)

    return encode_base62(decimal_signature)


def create_storage_content_signature(
    resource_id: str,
    url_signing_secret_key: str,
    *,
    expires_in: timedelta | None = None,
    version: int = 0,
) -> str:
    """Create a secure signature for a storage resource like a dataset or key-value store.

    This signature is used to generate a signed URL for authenticated access, which can be expiring or permanent.
    The signature is created using HMAC with the provided secret key and includes the resource ID, expiration time,
    and version.

    Args:
        resource_id: The unique identifier of the storage resource.
        url_signing_secret_key: The secret key for signing the URL.
        expires_in: Optional expiration duration; if None, the signature never expires.
        version: The signature version number (default: 0).

    Returns:
        The base64url-encoded signature string.
    """
    expires_at = int(time.time() * 1000) + int(to_seconds(expires_in) * 1000) if expires_in is not None else 0

    message_to_sign = f'{version}.{expires_at}.{resource_id}'
    hmac_sig = create_hmac_signature(url_signing_secret_key, message_to_sign)

    base64url_encoded_payload = urlsafe_b64encode(f'{version}.{expires_at}.{hmac_sig}'.encode())
    return base64url_encoded_payload.decode('utf-8')
