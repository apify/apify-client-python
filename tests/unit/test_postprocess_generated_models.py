from __future__ import annotations

import textwrap

from scripts.postprocess_generated_models import (
    add_docs_group_decorators,
    deduplicate_error_type_enum,
    fix_discriminators,
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
