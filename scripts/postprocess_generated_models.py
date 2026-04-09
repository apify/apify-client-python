"""Post-process the generated _models.py to fix known datamodel-codegen issues.

Currently fixes:
- Discriminator field names: datamodel-codegen sometimes emits the JSON property name (camelCase)
  instead of the Python field name (snake_case) in `Field(discriminator='...')` annotations,
  particularly when the discriminator is on a schema referenced inside array items.
- Duplicate ErrorType enum: ErrorResponse.yaml inlines the ErrorType enum (due to a Spectral
  nested-$ref limitation), causing datamodel-codegen to generate a duplicate `Type(StrEnum)`
  class alongside the canonical `ErrorType(StrEnum)`. This script removes the duplicate and
  rewires references to use `ErrorType`.
"""

from __future__ import annotations

import re
from pathlib import Path

MODELS_PATH = Path(__file__).resolve().parent.parent / 'src' / 'apify_client' / '_models.py'

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


def main() -> None:
    content = MODELS_PATH.read_text()
    fixed = fix_discriminators(content)
    fixed = deduplicate_error_type_enum(fixed)

    if fixed != content:
        MODELS_PATH.write_text(fixed)
        print(f'Fixed generated models in {MODELS_PATH}')
    else:
        print('No fixes needed')


if __name__ == '__main__':
    main()
