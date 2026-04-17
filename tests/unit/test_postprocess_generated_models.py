from __future__ import annotations

import textwrap

import pytest

from scripts.postprocess_generated_models import (
    add_docs_group_decorators,
    deduplicate_error_type_enum,
    derive_exception_class_names,
    extract_error_type_members,
    fix_discriminators,
    render_generated_errors_module,
)

# -- fix_discriminators -------------------------------------------------------


def test_fix_discriminators_replaces_camel_case() -> None:
    content = "items: list[Pricing] = Field(discriminator='pricingModel')"
    result = fix_discriminators(content)
    assert result == "items: list[Pricing] = Field(discriminator='pricing_model')"


def test_fix_discriminators_replaces_multiple_occurrences() -> None:
    content = "a: list[X] = Field(discriminator='pricingModel')\nb: list[Y] = Field(discriminator='pricingModel')\n"
    result = fix_discriminators(content)
    assert "discriminator='pricingModel'" not in result
    assert result.count("discriminator='pricing_model'") == 2


def test_fix_discriminators_leaves_already_snake_case() -> None:
    content = "items: list[Pricing] = Field(discriminator='pricing_model')"
    result = fix_discriminators(content)
    assert result == content


def test_fix_discriminators_no_change_when_no_discriminators() -> None:
    content = 'class Foo(BaseModel):\n    name: str\n'
    result = fix_discriminators(content)
    assert result == content


def test_fix_discriminators_does_not_touch_unrelated() -> None:
    content = "items: list[X] = Field(discriminator='event_type')"
    result = fix_discriminators(content)
    assert result == content


# -- deduplicate_error_type_enum ----------------------------------------------


def test_deduplicate_error_type_enum_removes_duplicate() -> None:
    content = textwrap.dedent("""\
        class ErrorType(StrEnum):
            SOME_ERROR = 'some-error'

        class Type(StrEnum):
            SOME_ERROR = 'some-error'
            OTHER = 'other'

        class ErrorResponse(BaseModel):
            error_type: Type
    """)
    result = deduplicate_error_type_enum(content)
    assert 'class Type(StrEnum)' not in result
    assert 'class ErrorType(StrEnum)' in result


def test_deduplicate_error_type_enum_rewires_colon_annotation() -> None:
    content = textwrap.dedent("""\
        class ErrorType(StrEnum):
            SOME_ERROR = 'some-error'

        class Type(StrEnum):
            SOME_ERROR = 'some-error'

        class ErrorResponse(BaseModel):
            error_type: Type
    """)
    result = deduplicate_error_type_enum(content)
    assert 'error_type: ErrorType' in result


def test_deduplicate_error_type_enum_rewires_union_annotation() -> None:
    content = textwrap.dedent("""\
        class ErrorType(StrEnum):
            X = 'x'

        class Type(StrEnum):
            X = 'x'

        class Foo(BaseModel):
            field: str | Type
    """)
    result = deduplicate_error_type_enum(content)
    assert '| ErrorType' in result
    assert '| Type' not in result


def test_deduplicate_error_type_enum_rewires_bracket_annotation() -> None:
    content = textwrap.dedent("""\
        class ErrorType(StrEnum):
            X = 'x'

        class Type(StrEnum):
            X = 'x'

        class Foo(BaseModel):
            field: list[Type]
    """)
    result = deduplicate_error_type_enum(content)
    assert 'list[ErrorType]' in result
    assert 'list[Type]' not in result


def test_deduplicate_error_type_enum_collapses_extra_blank_lines() -> None:
    content = "\nclass Type(StrEnum):\n    X = 'x'\n\n\n\n\nclass Next(BaseModel):\n    pass\n"
    result = deduplicate_error_type_enum(content)
    assert '\n\n\n\n' not in result


def test_deduplicate_error_type_enum_no_change_when_no_duplicate() -> None:
    content = textwrap.dedent("""\
        class ErrorType(StrEnum):
            SOME_ERROR = 'some-error'

        class Foo(BaseModel):
            field: ErrorType
    """)
    result = deduplicate_error_type_enum(content)
    assert result == content


def test_deduplicate_error_type_enum_does_not_touch_type_in_class_names() -> None:
    """Ensure `Type` in class names like `ContentType` is not replaced."""
    content = textwrap.dedent("""\
        class ErrorType(StrEnum):
            X = 'x'

        class Type(StrEnum):
            X = 'x'

        class ContentType(BaseModel):
            value: str
    """)
    result = deduplicate_error_type_enum(content)
    assert 'class ContentType(BaseModel)' in result


# -- add_docs_group_decorators ------------------------------------------------


def test_add_docs_group_decorators_adds_import_and_decorators() -> None:
    content = textwrap.dedent("""\
        from pydantic import BaseModel

        class Foo(BaseModel):
            name: str

        class Bar(BaseModel):
            value: int
    """)
    result = add_docs_group_decorators(content)
    assert 'from apify_client._docs import docs_group' in result
    assert result.count("@docs_group('Models')") == 2


def test_add_docs_group_decorators_places_import_after_pydantic() -> None:
    content = textwrap.dedent("""\
        from pydantic import BaseModel

        class Foo(BaseModel):
            pass
    """)
    result = add_docs_group_decorators(content)
    lines = result.split('\n')
    pydantic_idx = next(i for i, line in enumerate(lines) if 'from pydantic' in line)
    docs_import_idx = next(i for i, line in enumerate(lines) if 'from apify_client._docs' in line)
    assert docs_import_idx == pydantic_idx + 2  # blank line + import


def test_add_docs_group_decorators_idempotent_import() -> None:
    content = textwrap.dedent("""\
        from pydantic import BaseModel

        from apify_client._docs import docs_group

        class Foo(BaseModel):
            pass
    """)
    result = add_docs_group_decorators(content)
    assert result.count('from apify_client._docs import docs_group') == 1


def test_add_docs_group_decorators_idempotent_decorators() -> None:
    content = textwrap.dedent("""\
        from pydantic import BaseModel

        from apify_client._docs import docs_group

        @docs_group('Models')
        class Foo(BaseModel):
            pass

        @docs_group('Models')
        class Bar(BaseModel):
            pass
    """)
    result = add_docs_group_decorators(content)
    assert result.count("@docs_group('Models')") == 2


def test_add_docs_group_decorators_placed_before_each_class() -> None:
    content = textwrap.dedent("""\
        from pydantic import BaseModel

        class Alpha(BaseModel):
            pass

        class Beta(BaseModel):
            pass
    """)
    result = add_docs_group_decorators(content)
    lines = result.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('class '):
            assert lines[i - 1] == "@docs_group('Models')"


def test_add_docs_group_decorators_no_classes() -> None:
    content = 'from pydantic import BaseModel\n\nx = 1\n'
    result = add_docs_group_decorators(content)
    assert "@docs_group('Models')" not in result


# -- Integration: full pipeline -----------------------------------------------


def test_full_pipeline() -> None:
    content = textwrap.dedent("""\
        from pydantic import BaseModel

        class Zebra(BaseModel):
            items: list[Pricing] = Field(discriminator='pricingModel')

        class ErrorType(StrEnum):
            SOME_ERROR = 'some-error'

        class Type(StrEnum):
            SOME_ERROR = 'some-error'

        class ErrorResponse(BaseModel):
            error_type: Type

        class Alpha(BaseModel):
            name: str
    """)
    result = fix_discriminators(content)
    result = deduplicate_error_type_enum(result)
    result = add_docs_group_decorators(result)

    # Discriminator fixed.
    assert "discriminator='pricing_model'" in result
    assert "discriminator='pricingModel'" not in result

    # Duplicate Type enum removed and references rewired.
    assert 'class Type(StrEnum)' not in result
    assert 'error_type: ErrorType' in result

    # Decorators added.
    assert "@docs_group('Models')" in result


# -- extract_error_type_members -----------------------------------------------


def test_extract_error_type_members_returns_name_value_pairs() -> None:
    content = textwrap.dedent("""\
        from enum import StrEnum

        class ErrorType(StrEnum):
            RECORD_NOT_FOUND = 'record-not-found'
            ACTOR_NOT_FOUND = 'actor-not-found'
    """)
    members = extract_error_type_members(content)
    assert members == [('RECORD_NOT_FOUND', 'record-not-found'), ('ACTOR_NOT_FOUND', 'actor-not-found')]


def test_extract_error_type_members_ignores_other_classes() -> None:
    content = textwrap.dedent("""\
        from enum import StrEnum

        class OtherEnum(StrEnum):
            FOO = 'foo'

        class ErrorType(StrEnum):
            BAR = 'bar'
    """)
    assert extract_error_type_members(content) == [('BAR', 'bar')]


def test_extract_error_type_members_returns_empty_when_missing() -> None:
    content = 'from enum import StrEnum\n\nclass Foo(StrEnum):\n    A = "a"\n'
    assert extract_error_type_members(content) == []


# -- derive_exception_class_names ---------------------------------------------


def test_derive_exception_class_names_strips_error_suffix() -> None:
    members = [('BILLING_SYSTEM_ERROR', 'billing-system-error')]
    assert derive_exception_class_names(members) == [
        ('BILLING_SYSTEM_ERROR', 'billing-system-error', 'BillingSystemError'),
    ]


def test_derive_exception_class_names_appends_error_when_absent() -> None:
    members = [('RECORD_NOT_FOUND', 'record-not-found')]
    assert derive_exception_class_names(members) == [
        ('RECORD_NOT_FOUND', 'record-not-found', 'RecordNotFoundError'),
    ]


def test_derive_exception_class_names_preserves_digit_parts() -> None:
    members = [
        ('FIELD_3D_SECURE_AUTH_FAILED', '3d-secure-auth-failed'),
        ('X402_PAYMENT_REQUIRED', 'x402-payment-required'),
    ]
    result = derive_exception_class_names(members)
    assert result[0][2] == 'Field3DSecureAuthFailedError'
    assert result[1][2] == 'X402PaymentRequiredError'


def test_derive_exception_class_names_resolves_stripping_collision() -> None:
    # `SCHEMA_VALIDATION` comes first and claims `SchemaValidationError`.
    # `SCHEMA_VALIDATION_ERROR` collides after stripping and falls back to the full-name variant.
    members = [
        ('SCHEMA_VALIDATION', 'schema-validation'),
        ('SCHEMA_VALIDATION_ERROR', 'schema-validation-error'),
    ]
    result = derive_exception_class_names(members)
    assert result == [
        ('SCHEMA_VALIDATION', 'schema-validation', 'SchemaValidationError'),
        ('SCHEMA_VALIDATION_ERROR', 'schema-validation-error', 'SchemaValidationErrorError'),
    ]


def test_derive_exception_class_names_raises_on_unresolvable_collision() -> None:
    # Identical names must surface an error rather than silently dropping one.
    members = [('FOO', 'foo'), ('FOO', 'foo-2')]
    with pytest.raises(RuntimeError, match='Cannot derive a unique'):
        derive_exception_class_names(members)


# -- render_generated_errors_module -------------------------------------------


def test_render_generated_errors_module_emits_classes_and_dispatch_map() -> None:
    rendered = render_generated_errors_module(
        [
            ('RECORD_NOT_FOUND', 'record-not-found', 'RecordNotFoundError'),
            ('ACTOR_NOT_FOUND', 'actor-not-found', 'ActorNotFoundError'),
        ]
    )
    assert 'from apify_client.errors import ApifyApiError' in rendered
    assert 'class RecordNotFoundError(ApifyApiError):' in rendered
    assert 'class ActorNotFoundError(ApifyApiError):' in rendered
    assert "'record-not-found': RecordNotFoundError," in rendered
    assert "'actor-not-found': ActorNotFoundError," in rendered
    assert "@docs_group('Errors')" in rendered
    assert "'RecordNotFoundError'," in rendered  # __all__ entry


def test_render_generated_errors_module_is_syntactically_valid() -> None:
    rendered = render_generated_errors_module([('RECORD_NOT_FOUND', 'record-not-found', 'RecordNotFoundError')])
    # Raises SyntaxError if the rendered source is malformed.
    compile(rendered, '<generated>', 'exec')
