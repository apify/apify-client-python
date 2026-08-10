from __future__ import annotations

from pydantic import BaseModel

from apify_client import _models


def test_url_fields_are_plain_strings() -> None:
    """URL fields must be typed `str`, not `pydantic.AnyUrl`, so values pass through exactly as the API sent them.

    `AnyUrl` normalizes URLs during validation (e.g. appends a trailing slash to a URL without a path), silently
    changing the value the server sent. The `type_mappings` entry in `[tool.datamodel-codegen]` keeps `format: uri`
    fields as plain strings; this test guards that setting against being lost in a future regeneration.

    https://github.com/apify/apify-client-python/issues/999
    """
    offenders = [
        f'{obj.__name__}.{field_name}'
        for obj in vars(_models).values()
        if isinstance(obj, type) and issubclass(obj, BaseModel)
        for field_name, field in obj.model_fields.items()
        if 'AnyUrl' in str(field.annotation)
    ]
    assert offenders == []
