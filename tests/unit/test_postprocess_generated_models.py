from __future__ import annotations

import textwrap

from scripts.postprocess_generated_models import (
    add_docs_group_decorators,
    convert_enums_to_literals,
    deduplicate_error_type_enum,
    fix_discriminators,
    split_literals_to_file,
)

# -- fix_discriminators -------------------------------------------------------


def test_fix_discriminators_replaces_camel_case() -> None:
    """A camelCase discriminator value is rewritten to its snake_case form."""
    content = "items: list[Pricing] = Field(discriminator='pricingModel')"
    result = fix_discriminators(content)
    assert result == "items: list[Pricing] = Field(discriminator='pricing_model')"


def test_fix_discriminators_replaces_multiple_occurrences() -> None:
    """Every occurrence of a known camelCase discriminator is rewritten, not just the first."""
    content = "a: list[X] = Field(discriminator='pricingModel')\nb: list[Y] = Field(discriminator='pricingModel')\n"
    result = fix_discriminators(content)
    assert "discriminator='pricingModel'" not in result
    assert result.count("discriminator='pricing_model'") == 2


def test_fix_discriminators_leaves_already_snake_case() -> None:
    """A discriminator already in snake_case is left untouched."""
    content = "items: list[Pricing] = Field(discriminator='pricing_model')"
    result = fix_discriminators(content)
    assert result == content


def test_fix_discriminators_no_change_when_no_discriminators() -> None:
    """Source with no discriminators at all passes through unchanged."""
    content = 'class Foo(BaseModel):\n    name: str\n'
    result = fix_discriminators(content)
    assert result == content


def test_fix_discriminators_does_not_touch_unrelated() -> None:
    """A discriminator value that is not in the known map is not rewritten."""
    content = "items: list[X] = Field(discriminator='event_type')"
    result = fix_discriminators(content)
    assert result == content


# -- deduplicate_error_type_enum ----------------------------------------------


def test_deduplicate_error_type_enum_removes_duplicate() -> None:
    """The duplicate `Type(StrEnum)` is dropped while the original `ErrorType` is preserved."""
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
    """A `: Type` annotation is rewired to `: ErrorType` after the duplicate is dropped."""
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
    """A `| Type` arm in a union annotation is rewired to `| ErrorType`."""
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
    """A `[Type]` subscript inside a generic annotation is rewired to `[ErrorType]`."""
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
    """Removing the duplicate enum collapses any resulting run of 4+ blank lines."""
    content = "\nclass Type(StrEnum):\n    X = 'x'\n\n\n\n\nclass Next(BaseModel):\n    pass\n"
    result = deduplicate_error_type_enum(content)
    assert '\n\n\n\n' not in result


def test_deduplicate_error_type_enum_no_change_when_no_duplicate() -> None:
    """Source without a `Type(StrEnum)` duplicate passes through unchanged."""
    content = textwrap.dedent("""\
        class ErrorType(StrEnum):
            SOME_ERROR = 'some-error'

        class Foo(BaseModel):
            field: ErrorType
    """)
    result = deduplicate_error_type_enum(content)
    assert result == content


def test_deduplicate_error_type_enum_does_not_touch_type_in_class_names() -> None:
    """`Type` inside other class names (e.g. `ContentType`) is not rewritten."""
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


def test_deduplicate_error_type_enum_handles_type_as_last_class() -> None:
    """The `Type` enum is removed even when it's the last top-level definition."""
    content = textwrap.dedent("""\
        class ErrorType(StrEnum):
            X = 'x'

        class Foo(BaseModel):
            field: Type

        class Type(StrEnum):
            X = 'x'
    """)
    result = deduplicate_error_type_enum(content)
    assert 'class Type(StrEnum)' not in result
    assert 'field: ErrorType' in result


def test_deduplicate_error_type_enum_skips_non_strenum_type() -> None:
    """A `Type` class that is not a `StrEnum` (e.g. a Pydantic model) is left in place."""
    content = textwrap.dedent("""\
        class ErrorType(StrEnum):
            X = 'x'

        class Type(BaseModel):
            value: str
    """)
    result = deduplicate_error_type_enum(content)
    assert 'class Type(BaseModel)' in result


# -- add_docs_group_decorators ------------------------------------------------


def test_add_docs_group_decorators_adds_import_and_decorators() -> None:
    """Both the `docs_group` import and a decorator on every class are inserted."""
    content = textwrap.dedent("""\
        from pydantic import BaseModel

        class Foo(BaseModel):
            name: str

        class Bar(BaseModel):
            value: int
    """)
    result = add_docs_group_decorators(content, 'Models')
    assert 'from apify_client._docs import docs_group' in result
    assert result.count("@docs_group('Models')") == 2


def test_add_docs_group_decorators_places_import_after_pydantic() -> None:
    """The injected `docs_group` import lands directly after the existing `from pydantic` line."""
    content = textwrap.dedent("""\
        from pydantic import BaseModel

        class Foo(BaseModel):
            pass
    """)
    result = add_docs_group_decorators(content, 'Models')
    lines = result.split('\n')
    pydantic_idx = next(i for i, line in enumerate(lines) if 'from pydantic' in line)
    docs_import_idx = next(i for i, line in enumerate(lines) if 'from apify_client._docs' in line)
    assert docs_import_idx == pydantic_idx + 2  # blank line + import


def test_add_docs_group_decorators_idempotent_import() -> None:
    """Re-running the step doesn't duplicate the `docs_group` import."""
    content = textwrap.dedent("""\
        from pydantic import BaseModel

        from apify_client._docs import docs_group

        class Foo(BaseModel):
            pass
    """)
    result = add_docs_group_decorators(content, 'Models')
    assert result.count('from apify_client._docs import docs_group') == 1


def test_add_docs_group_decorators_idempotent_decorators() -> None:
    """Re-running the step doesn't add a second decorator above an already-decorated class."""
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
    result = add_docs_group_decorators(content, 'Models')
    assert result.count("@docs_group('Models')") == 2


def test_add_docs_group_decorators_placed_before_each_class() -> None:
    """Every `class` line is immediately preceded by the decorator line."""
    content = textwrap.dedent("""\
        from pydantic import BaseModel

        class Alpha(BaseModel):
            pass

        class Beta(BaseModel):
            pass
    """)
    result = add_docs_group_decorators(content, 'Models')
    lines = result.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('class '):
            assert lines[i - 1] == "@docs_group('Models')"


def test_add_docs_group_decorators_no_classes() -> None:
    """Source with no classes gets no decorators inserted."""
    content = 'from pydantic import BaseModel\n\nx = 1\n'
    result = add_docs_group_decorators(content, 'Models')
    assert "@docs_group('Models')" not in result


# -- convert_enums_to_literals ------------------------------------------------


def test_convert_enums_to_literals_replaces_single_enum() -> None:
    """A `StrEnum` class becomes a `Name = Literal[...]` alias carrying the same string values."""
    content = textwrap.dedent("""\
        from enum import StrEnum
        from typing import Literal

        class Status(StrEnum):
            READY = 'READY'
            RUNNING = 'RUNNING'
    """)
    result = convert_enums_to_literals(content)
    assert 'class Status(StrEnum)' not in result
    assert 'Status = Literal[' in result
    assert "'READY'," in result
    assert "'RUNNING'," in result


def test_convert_enums_to_literals_preserves_value_order() -> None:
    """Literal values appear in the alias in the same order as the enum's member declarations."""
    content = textwrap.dedent("""\
        from typing import Literal

        class Status(StrEnum):
            SECOND = 'second'
            FIRST = 'first'
            THIRD = 'third'
    """)
    result = convert_enums_to_literals(content)
    second_idx = result.index("'second'")
    first_idx = result.index("'first'")
    third_idx = result.index("'third'")
    assert second_idx < first_idx < third_idx


def test_convert_enums_to_literals_preserves_docstring() -> None:
    """The class docstring is kept as a trailing bare-string after the alias."""
    content = textwrap.dedent("""\
        from typing import Literal

        class Status(StrEnum):
            \"\"\"Describes a status.\"\"\"

            READY = 'READY'
    """)
    result = convert_enums_to_literals(content)
    assert '"""Describes a status."""' in result
    # Docstring must appear AFTER the type alias, not before.
    alias_idx = result.index('Status = Literal[')
    docstring_idx = result.index('"""Describes a status."""')
    assert alias_idx < docstring_idx


def test_convert_enums_to_literals_preserves_hyphenated_values() -> None:
    """The string values are taken verbatim — hyphenated values like `'TIMED-OUT'` survive intact."""
    content = textwrap.dedent("""\
        from typing import Literal

        class Status(StrEnum):
            TIMED_OUT = 'TIMED-OUT'
            TIMING_OUT = 'TIMING-OUT'
    """)
    result = convert_enums_to_literals(content)
    assert "'TIMED-OUT'," in result
    assert "'TIMING-OUT'," in result
    # The enum-member name (TIMED_OUT) should not appear in the output.
    assert 'TIMED_OUT' not in result


def test_convert_enums_to_literals_handles_multiple_enums() -> None:
    """Multiple `StrEnum` classes in the same file are each converted independently."""
    content = textwrap.dedent("""\
        from typing import Literal

        class Alpha(StrEnum):
            A = 'a'

        class Beta(StrEnum):
            B = 'b'
    """)
    result = convert_enums_to_literals(content)
    assert 'Alpha = Literal[' in result
    assert 'Beta = Literal[' in result
    assert 'class Alpha(StrEnum)' not in result
    assert 'class Beta(StrEnum)' not in result


def test_convert_enums_to_literals_skips_non_strenum_classes() -> None:
    """Classes whose bases don't include `StrEnum` (e.g. Pydantic models) are not touched."""
    content = textwrap.dedent("""\
        from typing import Literal

        class Foo(BaseModel):
            name: str

        class Status(StrEnum):
            A = 'a'
    """)
    result = convert_enums_to_literals(content)
    assert 'class Foo(BaseModel)' in result
    assert 'class Status(StrEnum)' not in result


def test_convert_enums_to_literals_no_change_when_no_enums() -> None:
    """Source without any `StrEnum` class is returned byte-for-byte unchanged."""
    content = textwrap.dedent("""\
        from typing import Literal

        class Foo(BaseModel):
            name: str
    """)
    result = convert_enums_to_literals(content)
    assert result == content


def test_convert_enums_to_literals_field_references_still_resolve() -> None:
    """Field annotations referencing the enum name still resolve since the alias keeps that name."""
    content = textwrap.dedent("""\
        from typing import Literal

        class Foo(BaseModel):
            status: Status

        class Status(StrEnum):
            A = 'a'
            B = 'b'
    """)
    result = convert_enums_to_literals(content)
    # Field still references the name; the name is now a type alias below.
    assert 'status: Status' in result
    assert 'Status = Literal[' in result


# -- Integration: full pipeline -----------------------------------------------


def test_full_pipeline() -> None:
    """All steps composed: discriminator fix, `Type` dedup, enum-to-literal, docs decorators."""
    content = textwrap.dedent("""\
        from enum import StrEnum
        from typing import Literal

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
    result = convert_enums_to_literals(result)
    result = add_docs_group_decorators(result, 'Models')

    # Discriminator fixed.
    assert "discriminator='pricing_model'" in result
    assert "discriminator='pricingModel'" not in result

    # Duplicate Type enum removed and references rewired, then the remaining enum converted.
    assert 'class Type(StrEnum)' not in result
    assert 'class ErrorType(StrEnum)' not in result
    assert 'ErrorType = Literal[' in result
    assert 'error_type: ErrorType' in result

    # Decorators added to real models but not to the type alias.
    assert result.count("@docs_group('Models')") == 3  # Zebra, ErrorResponse, Alpha


# -- split_literals_to_file ---------------------------------------------------


def test_split_literals_to_file_moves_literal_aliases() -> None:
    """The `Literal[...]` block plus its docstring move to the literals file; the models file imports it back."""
    content = textwrap.dedent("""\
        from __future__ import annotations

        from typing import Literal

        from pydantic import BaseModel

        from apify_client._docs import docs_group


        class Alpha(BaseModel):
            status: Status


        Status = Literal[
            'READY',
            'RUNNING',
        ]
        \"\"\"Alpha status docstring.\"\"\"
    """)
    models, literals = split_literals_to_file(content)

    assert 'Status = Literal[' not in models
    assert 'from apify_client._literals import Status' in models
    assert 'status: Status' in models  # field annotation still references the name

    assert 'Status = Literal[' in literals
    assert "'READY'" in literals
    assert '"""Alpha status docstring."""' in literals


def test_split_literals_to_file_handles_multiple_aliases() -> None:
    """Several aliases all move out and are re-imported together in a single import line."""
    content = textwrap.dedent("""\
        from __future__ import annotations

        from typing import Literal

        from apify_client._docs import docs_group


        A = Literal[
            'x',
        ]

        B = Literal[
            'y',
        ]
    """)
    models, literals = split_literals_to_file(content)

    assert 'A = Literal[' not in models
    assert 'B = Literal[' not in models
    assert 'from apify_client._literals import A, B' in models

    assert "A = Literal[\n    'x',\n]" in literals
    assert "B = Literal[\n    'y',\n]" in literals


def test_split_literals_to_file_no_literals_returns_original() -> None:
    """Source with no `Literal[...]` aliases yields the original models content and an empty literals string."""
    content = textwrap.dedent("""\
        from __future__ import annotations

        from pydantic import BaseModel

        from apify_client._docs import docs_group


        class Alpha(BaseModel):
            name: str
    """)
    models, literals = split_literals_to_file(content)
    assert models == content
    assert literals == ''


def test_split_literals_to_file_output_has_valid_header() -> None:
    """The generated literals file starts with the standard `from __future__` and `from typing` imports."""
    content = textwrap.dedent("""\
        from __future__ import annotations

        from typing import Literal

        from apify_client._docs import docs_group


        A = Literal['x']
    """)
    _, literals = split_literals_to_file(content)
    assert 'from __future__ import annotations' in literals
    assert 'from typing import Literal' in literals
