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
- Class sorting: Sorts class definitions alphabetically (with topological ordering to respect
  inheritance dependencies), so that regeneration from a reordered OpenAPI spec produces
  minimal diffs.
"""

from __future__ import annotations

import heapq
import re
from collections import defaultdict
from pathlib import Path

MODELS_PATH = Path(__file__).resolve().parent.parent / 'src' / 'apify_client' / '_models.py'
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

    This function is idempotent — it skips the import and decorators if they
    already exist.
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


def sort_classes(content: str) -> str:
    """Sort class definitions alphabetically while respecting inheritance order.

    Uses topological sorting so that base classes always appear before their
    subclasses, with alphabetical ordering as the tie-breaker.  This makes the
    output deterministic regardless of the order in the OpenAPI spec, which
    keeps diffs minimal across regenerations.

    Only the class statement's base-class expression creates an ordering
    constraint — field type annotations are lazy strings thanks to
    ``from __future__ import annotations`` and don't require forward
    declaration.
    """
    lines = content.split('\n')

    # Find where class blocks start (first @docs_group decorator).
    header_end = 0
    for i, line in enumerate(lines):
        if line == DOCS_GROUP_DECORATOR:
            header_end = i
            break

    # Strip trailing blank lines from the header; we re-add spacing later.
    header_lines = lines[:header_end]
    while header_lines and not header_lines[-1].strip():
        header_lines.pop()
    header = '\n'.join(header_lines)

    # Split the remainder into class blocks.
    # Each block starts with ``@docs_group('Models')`` on its own line.
    rest = '\n'.join(lines[header_end:])
    decorator_escaped = re.escape(DOCS_GROUP_DECORATOR)
    raw_blocks = re.split(rf'(?=^{decorator_escaped}$)', rest, flags=re.MULTILINE)
    blocks = [b.strip() for b in raw_blocks if b.strip()]

    # Parse each block: extract class name and base-class dependencies.
    class_blocks: dict[str, str] = {}
    class_deps: dict[str, set[str]] = {}

    for block in blocks:
        match = re.search(r'^class\s+(\w+)\(([^)]+)\):', block, re.MULTILINE)
        if not match:
            continue
        class_name = match.group(1)
        base_expr = match.group(2)
        # Collect all capitalized identifiers from the base-class expression.
        referenced = set(re.findall(r'\b([A-Z]\w+)\b', base_expr))
        class_blocks[class_name] = block
        class_deps[class_name] = referenced

    if len(class_blocks) != len(blocks):
        # Some blocks didn't match the class regex — fall back to avoid data loss.
        return content

    all_names = set(class_blocks)

    # Build the dependency graph (only in-file references matter).
    in_degree: dict[str, int] = {}
    reverse: dict[str, set[str]] = defaultdict(set)

    for name, refs in class_deps.items():
        local_deps = (refs & all_names) - {name}
        in_degree[name] = len(local_deps)
        for dep in local_deps:
            reverse[dep].add(name)

    # Kahn's algorithm with a min-heap for alphabetical tie-breaking.
    heap = sorted(name for name, degree in in_degree.items() if degree == 0)
    heapq.heapify(heap)

    sorted_names: list[str] = []
    while heap:
        name = heapq.heappop(heap)
        sorted_names.append(name)
        for dependent in reverse[name]:
            in_degree[dependent] -= 1
            if in_degree[dependent] == 0:
                heapq.heappush(heap, dependent)

    if len(sorted_names) != len(class_blocks):
        # Cycle detected — fall back to the original order to avoid data loss.
        return content

    sorted_blocks = [class_blocks[name] for name in sorted_names]
    return header + '\n\n\n' + '\n\n\n'.join(sorted_blocks) + '\n'


def main() -> None:
    content = MODELS_PATH.read_text()
    fixed = fix_discriminators(content)
    fixed = deduplicate_error_type_enum(fixed)
    fixed = add_docs_group_decorators(fixed)
    fixed = sort_classes(fixed)

    if fixed != content:
        MODELS_PATH.write_text(fixed)
        print(f'Fixed generated models in {MODELS_PATH}')
    else:
        print('No fixes needed')


if __name__ == '__main__':
    main()
