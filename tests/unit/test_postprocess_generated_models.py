from __future__ import annotations

import re
import textwrap

from scripts.postprocess_generated_models import (
    add_docs_group_decorators,
    deduplicate_error_type_enum,
    fix_discriminators,
    sort_classes,
)

# -- Helpers ------------------------------------------------------------------


def _make_file(header: str, classes: list[str]) -> str:
    """Build a fake models file with header and decorated class blocks."""
    parts = [header.rstrip()]
    parts.extend(f"@docs_group('Models')\n{cls}" for cls in classes)
    return '\n\n\n'.join(parts) + '\n'


def _extract_class_names(content: str) -> list[str]:
    """Extract class names in order of appearance."""
    return re.findall(r'^class\s+(\w+)\(', content, re.MULTILINE)


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


# -- sort_classes -------------------------------------------------------------


def test_sort_classes_alphabetically() -> None:
    content = _make_file(
        'from pydantic import BaseModel\n',
        [
            'class Charlie(BaseModel):\n    pass',
            'class Alpha(BaseModel):\n    pass',
            'class Bravo(BaseModel):\n    pass',
        ],
    )
    result = sort_classes(content)
    names = _extract_class_names(result)
    assert names == ['Alpha', 'Bravo', 'Charlie']


def test_sort_classes_respects_inheritance_order() -> None:
    """A child class must come after its parent, even if alphabetically first."""
    content = _make_file(
        'from pydantic import BaseModel\n',
        [
            'class Apple(Fruit):\n    pass',
            'class Fruit(BaseModel):\n    pass',
        ],
    )
    result = sort_classes(content)
    names = _extract_class_names(result)
    assert names.index('Fruit') < names.index('Apple')


def test_sort_classes_diamond_inheritance() -> None:
    content = _make_file(
        'from pydantic import BaseModel\n',
        [
            'class Diamond(Left, Right):\n    pass',
            'class Right(Base):\n    pass',
            'class Left(Base):\n    pass',
            'class Base(BaseModel):\n    pass',
        ],
    )
    result = sort_classes(content)
    names = _extract_class_names(result)
    assert names.index('Base') < names.index('Left')
    assert names.index('Base') < names.index('Right')
    assert names.index('Left') < names.index('Diamond')
    assert names.index('Right') < names.index('Diamond')


def test_sort_classes_alphabetical_tiebreaking() -> None:
    content = _make_file(
        'from pydantic import BaseModel\n',
        [
            'class Zulu(BaseModel):\n    pass',
            'class Mike(BaseModel):\n    pass',
            'class Alpha(BaseModel):\n    pass',
        ],
    )
    result = sort_classes(content)
    names = _extract_class_names(result)
    assert names == ['Alpha', 'Mike', 'Zulu']


def test_sort_classes_already_sorted_is_stable() -> None:
    content = _make_file(
        'from pydantic import BaseModel\n',
        [
            'class Alpha(BaseModel):\n    pass',
            'class Bravo(BaseModel):\n    pass',
            'class Charlie(BaseModel):\n    pass',
        ],
    )
    result = sort_classes(content)
    assert result == content


def test_sort_classes_preserves_header() -> None:
    header = 'from __future__ import annotations\n\nfrom pydantic import BaseModel\n\nX = 1\n'
    content = _make_file(
        header,
        [
            'class Bravo(BaseModel):\n    pass',
            'class Alpha(BaseModel):\n    pass',
        ],
    )
    result = sort_classes(content)
    assert result.startswith('from __future__ import annotations\n\nfrom pydantic import BaseModel\n\nX = 1')


def test_sort_classes_preserves_class_body() -> None:
    body_a = 'class Alpha(BaseModel):\n    name: str\n    age: int = 0'
    body_b = 'class Bravo(BaseModel):\n    value: float'
    content = _make_file('from pydantic import BaseModel\n', [body_b, body_a])
    result = sort_classes(content)
    assert body_a in result
    assert body_b in result


def test_sort_classes_chain_inheritance() -> None:
    """Child -> Parent -> GrandParent must preserve order GrandParent, Parent, Child."""
    content = _make_file(
        'from pydantic import BaseModel\n',
        [
            'class Child(Parent):\n    pass',
            'class Parent(GrandParent):\n    pass',
            'class GrandParent(BaseModel):\n    pass',
        ],
    )
    result = sort_classes(content)
    names = _extract_class_names(result)
    assert names == ['GrandParent', 'Parent', 'Child']


def test_sort_classes_ignores_external_base_classes() -> None:
    content = _make_file(
        'from pydantic import BaseModel\n',
        [
            'class Zeta(BaseModel):\n    pass',
            'class Alpha(BaseModel):\n    pass',
        ],
    )
    result = sort_classes(content)
    names = _extract_class_names(result)
    assert names == ['Alpha', 'Zeta']


def test_sort_classes_self_reference_in_base_ignored() -> None:
    """A class listing itself in the base expression should not deadlock."""
    content = _make_file(
        'from pydantic import BaseModel\n',
        [
            'class Foo(BaseModel):\n    pass',
        ],
    )
    result = sort_classes(content)
    assert 'class Foo(BaseModel)' in result


def test_sort_classes_single_class() -> None:
    content = _make_file(
        'from pydantic import BaseModel\n',
        [
            'class Only(BaseModel):\n    name: str',
        ],
    )
    result = sort_classes(content)
    assert 'class Only(BaseModel)' in result


def test_sort_classes_generic_base_class() -> None:
    """Classes with generic bases like RootModel[list[Foo]] should parse correctly."""
    content = _make_file(
        'from pydantic import BaseModel, RootModel\n',
        [
            'class FooList(RootModel[list[Foo]]):\n    pass',
            'class Foo(BaseModel):\n    name: str',
        ],
    )
    result = sort_classes(content)
    names = _extract_class_names(result)
    # Foo is referenced in FooList's base expression, so Foo must come first.
    assert names.index('Foo') < names.index('FooList')


def test_sort_classes_multiple_independent_trees() -> None:
    """Two separate inheritance trees should each be sorted correctly."""
    content = _make_file(
        'from pydantic import BaseModel\n',
        [
            'class DogBreed(Dog):\n    pass',
            'class Cat(BaseModel):\n    pass',
            'class Dog(BaseModel):\n    pass',
            'class Ant(BaseModel):\n    pass',
        ],
    )
    result = sort_classes(content)
    names = _extract_class_names(result)
    assert names.index('Dog') < names.index('DogBreed')
    # All independent classes should be in alphabetical order relative to each other.
    independent = [n for n in names if n != 'DogBreed']
    assert independent == sorted(independent)


def test_sort_classes_fallback_on_cycle() -> None:
    """If there's a cycle in inheritance, the original content is returned unchanged."""
    content = _make_file(
        'from pydantic import BaseModel\n',
        [
            'class A(B):\n    pass',
            'class B(A):\n    pass',
        ],
    )
    result = sort_classes(content)
    assert result == content


def test_sort_classes_fallback_on_unparsable_block() -> None:
    header = 'from pydantic import BaseModel'
    # Insert a decorated block that has no valid class definition.
    content = (
        f'{header}\n\n\n'
        f"@docs_group('Models')\n"
        f'# This is not a class\n'
        f'some_var = 1\n\n\n'
        f"@docs_group('Models')\n"
        f'class Foo(BaseModel):\n'
        f'    pass\n'
    )
    result = sort_classes(content)
    assert result == content


def test_sort_classes_multiline_class_body_preserved() -> None:
    """Ensure multi-line class bodies with various field types are fully preserved."""
    body = textwrap.dedent("""\
        class Config(BaseModel):
            name: str
            value: int = 0
            tags: list[str] = Field(default_factory=list)

            def validate_name(self) -> None:
                pass""")
    content = _make_file(
        'from pydantic import BaseModel, Field\n',
        [
            'class Zebra(BaseModel):\n    pass',
            body,
        ],
    )
    result = sort_classes(content)
    names = _extract_class_names(result)
    assert names == ['Config', 'Zebra']
    assert 'def validate_name(self) -> None:' in result


def test_sort_classes_strips_trailing_header_blanks() -> None:
    """Trailing blank lines in the header should not cause extra spacing."""
    content = _make_file(
        'from pydantic import BaseModel\n\n\n\n',
        [
            'class Foo(BaseModel):\n    pass',
        ],
    )
    result = sort_classes(content)
    # Should not have more than 3 consecutive newlines.
    assert '\n\n\n\n' not in result


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
    result = sort_classes(result)

    # Discriminator fixed.
    assert "discriminator='pricing_model'" in result
    assert "discriminator='pricingModel'" not in result

    # Duplicate Type enum removed and references rewired.
    assert 'class Type(StrEnum)' not in result
    assert 'error_type: ErrorType' in result

    # Decorators added.
    assert "@docs_group('Models')" in result

    # Classes sorted (Alpha before ErrorResponse before Zebra).
    names = _extract_class_names(result)
    model_names = [n for n in names if n != 'ErrorType']
    assert model_names == sorted(model_names)
