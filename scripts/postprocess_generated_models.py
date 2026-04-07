"""Post-process the generated _models.py to fix known datamodel-codegen issues.

Currently fixes:
- Discriminator field names: datamodel-codegen sometimes emits the JSON property name (camelCase)
  instead of the Python field name (snake_case) in `Field(discriminator='...')` annotations,
  particularly when the discriminator is on a schema referenced inside array items.
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


def main() -> None:
    content = MODELS_PATH.read_text()
    fixed = fix_discriminators(content)

    if fixed != content:
        MODELS_PATH.write_text(fixed)
        print(f'Fixed discriminator values in {MODELS_PATH}')
    else:
        print('No discriminator fixes needed')


if __name__ == '__main__':
    main()
