"""Utilities for creating secure signatures for storage access."""

from __future__ import annotations

import base64
import hashlib
import hmac
import string
import time


def encode_base62(num: int) -> str:
    """Encode the given number to base62.

    Args:
        num: The number to encode

    Returns:
        Base62 encoded string
    """
    charset = string.digits + string.ascii_letters

    if num == 0:
        return charset[0]

    res = ''
    while num > 0:
        num, remainder = divmod(num, 62)
        res = charset[remainder] + res
    return res


def create_hmac_signature(secret_key: str, message: str) -> str:
    """Generate an HMAC signature and encodes it using Base62.

    Base62 encoding reduces the signature length.
    HMAC signature is truncated to 30 characters to make it shorter.

    Args:
        secret_key: Secret key used for signing signatures.
        message: Message to be signed.

    Returns:
        Base62 encoded signature.
    """
    signature = hmac.new(secret_key.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).hexdigest()[:30]

    decimal_signature = int(signature, 16)

    return encode_base62(decimal_signature)


def create_storage_content_signature(
    resource_id: str,
    url_signing_secret_key: str,
    expires_in_millis: int | None = None,
    version: int = 0,
) -> str:
    """Create a secure signature for a resource like a dataset or key-value store.

    This signature is used to generate a signed URL for authenticated access,
    which can be expiring or permanent. The signature is created using HMAC
    with the provided secret key and includes the resource ID, expiration time,
    and version.

    Args:
        resource_id: The unique identifier of the resource.
        url_signing_secret_key: Secret key for signing the URL.
        expires_in_millis: Optional expiration time in milliseconds from now.
            If not provided, the signature will not expire.
        version: Signature version number (default: 0).

    Returns:
        Base64url encoded signature string.

    Note:
        expires_in_millis is optional. If not provided, the signature will not expire.
    """
    expires_at = int(time.time() * 1000) + expires_in_millis if expires_in_millis else 0

    message_to_sign = f'{version}.{expires_at}.{resource_id}'
    hmac_sig = create_hmac_signature(url_signing_secret_key, message_to_sign)

    base64url_encoded_payload = base64.urlsafe_b64encode(f'{version}.{expires_at}.{hmac_sig}'.encode())
    return base64url_encoded_payload.decode('utf-8')
