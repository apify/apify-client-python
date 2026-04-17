"""Post-process the generated _models.py to fix known datamodel-codegen issues.

Currently fixes:
- Discriminator field names: datamodel-codegen sometimes emits the JSON property name (camelCase)
  instead of the Python field name (snake_case) in `Field(discriminator='...')` annotations,
  particularly when the discriminator is on a schema referenced inside array items.
- Duplicate ErrorType enum: ErrorResponse.yaml inlines the ErrorType enum (due to a Spectral
  nested-$ref limitation), causing datamodel-codegen to generate a duplicate `Type(StrEnum)`
  class alongside the canonical `ErrorType(StrEnum)`. This script removes the duplicate and
  rewires references to use `ErrorType`.
- Missing @docs_group decorator: Adds `@docs_group('Models')` to all model classes for API
  reference documentation grouping, along with the required import.

Also generates `_generated_errors.py` — one `ApifyApiError` subclass per `ErrorType` enum member
plus a dispatch map used by `ApifyApiError.__new__` to return the specific subclass.
"""

from __future__ import annotations

import ast
import builtins
import re
from pathlib import Path

MODELS_PATH = Path(__file__).resolve().parent.parent / 'src' / 'apify_client' / '_models.py'
GENERATED_ERRORS_PATH = Path(__file__).resolve().parent.parent / 'src' / 'apify_client' / '_generated_errors.py'
DOCS_GROUP_DECORATOR = "@docs_group('Models')"

# Map of camelCase discriminator values to their snake_case equivalents.
# Add new entries here as needed when the OpenAPI spec introduces new discriminators.
DISCRIMINATOR_FIXES: dict[str, str] = {
    'pricingModel': 'pricing_model',
}


def fix_discriminators(content: str) -> str:
    """Replace camelCase discriminator values with their snake_case equivalents."""
    for camel, snake in DISCRIMINATOR_FIXES.items():
        content = re.sub(
            rf"discriminator='{camel}'",
            f"discriminator='{snake}'",
            content,
        )
    return content


def deduplicate_error_type_enum(content: str) -> str:
    """Remove the duplicate `Type` enum and rewire references to `ErrorType`."""
    # Remove the entire `class Type(StrEnum): ...` block up to the next class definition.
    content = re.sub(
        r'\nclass Type\(StrEnum\):.*?(?=\nclass )',
        '\n',
        content,
        flags=re.DOTALL,
    )
    # Replace standalone `Type` references in type annotations with `ErrorType`.
    # Only target annotation contexts (`: Type`, `| Type`, `[Type`).
    content = re.sub(r'(?<=: )Type\b|(?<=\| )Type\b|(?<=\[)Type\b', 'ErrorType', content)
    # Collapse triple+ blank lines left by the removal.
    return re.sub(r'\n{3,}', '\n\n\n', content)


def add_docs_group_decorators(content: str) -> str:
    """Add `@docs_group('Models')` decorator to all model classes and the required import.

    This function is idempotent — it skips the import and decorators if they already exist.
    """
    # Add the import after the existing imports (only if not already present).
    if 'from apify_client._docs import docs_group' not in content:
        content = re.sub(
            r'(from pydantic import [^\n]+\n)',
            r'\1\nfrom apify_client._docs import docs_group\n',
            content,
        )
    # Add @docs_group('Models') before class definitions not already preceded by it.
    lines = content.split('\n')
    result: list[str] = []
    for line in lines:
        if line.startswith('class ') and (not result or result[-1] != DOCS_GROUP_DECORATOR):
            result.append(DOCS_GROUP_DECORATOR)
        result.append(line)
    return '\n'.join(result)


def extract_error_type_members(content: str) -> list[tuple[str, str]]:
    """Parse `_models.py` and return `(member_name, member_value)` tuples for the `ErrorType` enum.

    Uses AST parsing for robustness against formatting differences. Returns an empty list if the
    `ErrorType` class is not found.
    """
    tree = ast.parse(content)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == 'ErrorType':
            return [
                (stmt.targets[0].id, stmt.value.value)
                for stmt in node.body
                if (
                    isinstance(stmt, ast.Assign)
                    and len(stmt.targets) == 1
                    and isinstance(stmt.targets[0], ast.Name)
                    and isinstance(stmt.value, ast.Constant)
                    and isinstance(stmt.value.value, str)
                )
            ]
    return []


def _pascal_case(name: str) -> str:
    """Convert `SCREAMING_SNAKE_CASE` to `PascalCase`, preserving all-caps parts that contain digits.

    Parts like `3D` or `X402` are left as-is so the result reads naturally (e.g.
    `FIELD_3D_SECURE` → `Field3DSecure` rather than `Field3dSecure`).
    """
    return ''.join(part if any(c.isdigit() for c in part) else part.capitalize() for part in name.split('_'))


def derive_exception_class_names(members: list[tuple[str, str]]) -> list[tuple[str, str, str]]:
    """Derive unique Exception class names for each `ErrorType` enum member.

    Strategy: strip a trailing `_ERROR` from the enum name and PascalCase the result, then append
    `Error`. If that collides with a previously derived name, always append `Error` to the full
    enum name — so `SCHEMA_VALIDATION` → `SchemaValidationError` (first wins) and
    `SCHEMA_VALIDATION_ERROR` falls back to `SchemaValidationErrorError`.

    Returns a list of `(member_name, member_value, class_name)` tuples.
    """
    taken: set[str] = set()
    builtin_names = set(dir(builtins))
    result: list[tuple[str, str, str]] = []
    for member_name, member_value in members:
        stripped = member_name.removesuffix('_ERROR')
        candidate = _pascal_case(stripped) + 'Error'
        if candidate in taken:
            candidate = _pascal_case(member_name) + 'Error'
        # Avoid shadowing builtins like `NotImplementedError` or `TimeoutError`.
        if candidate in builtin_names:
            candidate = 'Api' + candidate
        if candidate in taken:
            raise RuntimeError(
                f'Cannot derive a unique Exception class name for ErrorType.{member_name} '
                f'(value={member_value!r}); collides with an existing class. '
                'Extend derive_exception_class_names to handle this case.'
            )
        taken.add(candidate)
        result.append((member_name, member_value, candidate))
    return result


def render_generated_errors_module(classes: list[tuple[str, str, str]]) -> str:
    """Render the full `_generated_errors.py` source from the derived class list."""
    lines: list[str] = [
        '# generated by scripts/postprocess_generated_models.py -- do not edit manually',
        '"""Auto-generated Exception subclasses, one per `ErrorType` enum member.',
        '',
        'Each subclass inherits from `ApifyApiError` so existing `except ApifyApiError` handlers',
        'keep working. `ApifyApiError.__new__` uses `API_ERROR_CLASS_BY_TYPE` to dispatch to the',
        'specific subclass based on the `type` field of the API error response.',
        '"""',
        '',
        'from __future__ import annotations',
        '',
        'from apify_client._docs import docs_group',
        'from apify_client.errors import ApifyApiError',
        '',
    ]

    for _member_name, member_value, class_name in classes:
        lines.extend(
            [
                '',
                "@docs_group('Errors')",
                f'class {class_name}(ApifyApiError):',
                f'    """Raised when the Apify API returns a `{member_value}` error."""',
                '',
            ]
        )

    lines.extend(
        [
            '',
            'API_ERROR_CLASS_BY_TYPE: dict[str, type[ApifyApiError]] = {',
            *(f"    '{member_value}': {class_name}," for _, member_value, class_name in classes),
            '}',
            '',
            '',
            '__all__ = [',
            *(f"    '{name}'," for name in sorted(['API_ERROR_CLASS_BY_TYPE', *[c for _, _, c in classes]])),
            ']',
            '',
        ]
    )
    return '\n'.join(lines)


def write_generated_errors_module(content: str) -> bool:
    """Derive and write `_generated_errors.py`. Returns True if the file changed."""
    members = extract_error_type_members(content)
    if not members:
        return False
    classes = derive_exception_class_names(members)
    rendered = render_generated_errors_module(classes)
    previous = GENERATED_ERRORS_PATH.read_text() if GENERATED_ERRORS_PATH.exists() else ''
    if rendered != previous:
        GENERATED_ERRORS_PATH.write_text(rendered)
        return True
    return False


def main() -> None:
    content = MODELS_PATH.read_text()
    fixed = fix_discriminators(content)
    fixed = deduplicate_error_type_enum(fixed)
    fixed = add_docs_group_decorators(fixed)

    if fixed != content:
        MODELS_PATH.write_text(fixed)
        print(f'Fixed generated models in {MODELS_PATH}')
    else:
        print('No fixes needed')

    if write_generated_errors_module(fixed):
        print(f'Regenerated error classes in {GENERATED_ERRORS_PATH}')
    else:
        print('No error-class regeneration needed')


if __name__ == '__main__':
    main()
