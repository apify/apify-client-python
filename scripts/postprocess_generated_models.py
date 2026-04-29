"""Post-process datamodel-codegen output to fix known issues and prune the TypedDict file.

Applied to `_models.py`:
- Fix discriminator field names that use camelCase instead of snake_case (known issue with
  discriminators on schemas referenced from array items).
- Deduplicate the inlined `Type(StrEnum)` that comes from ErrorResponse.yaml; rewire to `ErrorType`.
- Add `@docs_group('Models')` to every model class (plus the required import).

Applied to `_typeddicts.py`:
- Keep only the TypedDicts actually used as resource-client method inputs (plus their transitive
  dependencies). The file is generated in full by datamodel-codegen; the trimming happens here.
- Rename every kept class to add a `Dict` suffix so it doesn't clash with the Pydantic model name
  (e.g. `WebhookCreate` -> `WebhookCreateDict`) and rewire references.
- Add `@docs_group('Typed dicts')` to every kept class.
"""

from __future__ import annotations

import ast
import re
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apify_client._docs import GroupName

REPO_ROOT = Path(__file__).resolve().parent.parent
PACKAGE_DIR = REPO_ROOT / 'src' / 'apify_client'
MODELS_PATH = PACKAGE_DIR / '_models.py'
TYPEDDICTS_PATH = PACKAGE_DIR / '_typeddicts.py'

# Map of camelCase discriminator values to their snake_case equivalents.
# Add new entries here as needed when the OpenAPI spec introduces new discriminators.
DISCRIMINATOR_FIXES: dict[str, str] = {
    'pricingModel': 'pricing_model',
}

# TypedDicts accepted as inputs by resource-client methods. These are the roots of the reachability
# walk over `_typeddicts.py`: anything not reachable from here (directly or transitively)
# is dropped so only the TypedDicts that are part of the public input surface — plus their nested
# shapes — survive. Names are the raw datamodel-codegen outputs (no `Dict` suffix yet); the suffix
# is added later by `rename_with_dict_suffix`. Update this set whenever a new `<Name>Dict | <Name>`
# union is introduced on a resource-client method signature.
RESOURCE_INPUT_TYPEDDICTS: frozenset[str] = frozenset(
    {
        'Request',  # RequestQueueClient.update_request
        'RequestDraft',  # RequestQueueClient.add_request, batch_add_requests
        'RequestDraftDelete',  # RequestQueueClient.batch_delete_requests
        'TaskInput',  # Actor/Task start/call/update default input
        'WebhookCreate',  # Actor/Task start/call webhook list element
        'WebhookRepresentation',  # Actor/Task start/call ad-hoc webhook list element
    }
)


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
    # Replace standalone `Type` references in annotation contexts (`: Type`, `| Type`, `[Type`).
    content = re.sub(r'(?<=: )Type\b|(?<=\| )Type\b|(?<=\[)Type\b', 'ErrorType', content)
    # Collapse triple+ blank lines left by the removal.
    return re.sub(r'\n{3,}', '\n\n\n', content)


def add_docs_group_decorators(content: str, group_name: GroupName) -> str:
    """Add `@docs_group(group_name)` to every class and inject the required import.

    Idempotent: skips classes that are already decorated and skips the import if it exists.
    """
    if 'from apify_client._docs import docs_group' not in content:
        content = re.sub(
            r'(from (?:pydantic|typing) import [^\n]+\n)',
            r'\1\nfrom apify_client._docs import docs_group\n',
            content,
            count=1,
        )

    decorator = f"@docs_group('{group_name}')"
    lines = content.split('\n')
    result: list[str] = []
    for line in lines:
        if line.startswith('class ') and (not result or result[-1] != decorator):
            result.append(decorator)
        result.append(line)
    return '\n'.join(result)


def flatten_empty_typeddicts(content: str) -> str:
    """Rewrite empty TypedDict classes into `ClassName: TypeAlias = dict[str, Any]`.

    An empty `TypedDict` is closed at the type-checker level (no keys allowed), which contradicts
    the open semantics of Pydantic models with `extra='allow'` and no declared fields (e.g.
    `TaskInput`). An open `dict[str, Any]` alias preserves the "any shape" contract.
    """
    tree = ast.parse(content)
    lines = content.split('\n')
    replaced = False
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        # A class body counts as "empty" if it has no fields — only optional docstring/pass/ellipsis.
        has_fields = any(
            isinstance(stmt, (ast.Assign, ast.AnnAssign, ast.FunctionDef, ast.AsyncFunctionDef)) for stmt in node.body
        )
        if has_fields:
            continue
        # Only flatten TypedDict-based classes (e.g. skip Enum subclasses).
        base_names = {b.id for b in node.bases if isinstance(b, ast.Name)}
        if 'TypedDict' not in base_names:
            continue
        assert node.end_lineno is not None  # noqa: S101
        start_idx = node.lineno - 1
        # Absorb a decorator that sits directly above the class definition (@docs_group).
        if start_idx > 0 and lines[start_idx - 1].lstrip().startswith('@'):
            start_idx -= 1
        for i in range(start_idx, node.end_lineno):
            lines[i] = ''
        lines[start_idx] = f'{node.name}: TypeAlias = dict[str, Any]'
        replaced = True

    if not replaced:
        return content

    output = re.sub(r'\n{3,}', '\n\n\n', '\n'.join(lines))
    # Flattening introduces new `TypeAlias` uses; make sure it's imported from typing.
    typing_import = re.search(r'from typing import[^\n]+', output)
    if typing_import is not None and 'TypeAlias' not in typing_import.group(0):
        output = re.sub(
            r'(from typing import )([^\n]+)',
            lambda m: f'{m.group(1)}{m.group(2)}, TypeAlias',
            output,
            count=1,
        )
    return output


def _is_string_expr(node: ast.stmt) -> bool:
    """Return True if `node` is a bare string expression (e.g. a module-level docstring)."""
    return isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str)


def _extract_top_level_symbols(tree: ast.Module) -> list[tuple[str, ast.stmt, int]]:
    """Return (name, node, end_line) for every top-level class or type-alias statement.

    If a top-level string expression immediately follows a symbol, it is absorbed into that
    symbol's `end_line` so they get pruned together (datamodel-codegen emits the schema description
    for TypeAlias statements as a bare string right after the alias).
    """
    symbols: list[tuple[str, ast.stmt, int]] = []
    body = tree.body
    i = 0
    while i < len(body):
        node = body[i]
        name: str | None = None
        if isinstance(node, ast.ClassDef):
            name = node.name
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            name = node.target.id

        if name is not None:
            assert node.end_lineno is not None  # noqa: S101
            end_line = node.end_lineno
            if i + 1 < len(body) and _is_string_expr(body[i + 1]):
                trailing = body[i + 1]
                assert trailing.end_lineno is not None  # noqa: S101
                end_line = trailing.end_lineno
                i += 1  # Skip the docstring: it's absorbed into this symbol.
            symbols.append((name, node, end_line))
        i += 1
    return symbols


def _collect_name_references(node: ast.AST, exclude: set[str]) -> set[str]:
    """Collect every `ast.Name` identifier under `node`, minus names in `exclude`."""
    refs: set[str] = set()
    for child in ast.walk(node):
        if isinstance(child, ast.Name):
            refs.add(child.id)
    return refs - exclude


def _compute_reachable_symbols(deps: dict[str, set[str]], seeds: set[str]) -> set[str]:
    """Return every symbol transitively reachable from any seed via `deps`."""
    reachable: set[str] = set()
    stack = [s for s in seeds if s in deps]
    while stack:
        name = stack.pop()
        if name in reachable:
            continue
        reachable.add(name)
        stack.extend(ref for ref in deps[name] if ref in deps and ref not in reachable)
    return reachable


def prune_typeddicts(content: str, seeds: frozenset[str]) -> tuple[str, set[str]]:
    """Remove every top-level class/alias not transitively reachable from `seeds`.

    Returns the pruned source and the set of names that were kept.
    """
    tree = ast.parse(content)
    symbols = _extract_top_level_symbols(tree)
    symbol_names = {name for name, _, _ in symbols}

    deps: dict[str, set[str]] = {}
    for name, node, _ in symbols:
        # Ignore builtins and imported names — we only care about cross-references within the file.
        deps[name] = _collect_name_references(node, exclude={name}) & symbol_names

    kept = _compute_reachable_symbols(deps, set(seeds))

    missing_seeds = seeds - symbol_names
    if missing_seeds:
        raise RuntimeError(f'TypedDict seeds missing from generated file: {sorted(missing_seeds)}')

    lines = content.split('\n')
    drop_line_indices: set[int] = set()
    for name, node, end_line in symbols:
        if name in kept:
            continue
        # ast line numbers are 1-indexed; list is 0-indexed.
        for line_no in range(node.lineno - 1, end_line):
            drop_line_indices.add(line_no)

    pruned = [line for i, line in enumerate(lines) if i not in drop_line_indices]
    output = '\n'.join(pruned)
    # Collapse runs of blank lines left behind by deletions.
    output = re.sub(r'\n{3,}', '\n\n\n', output)
    return output, kept


def rename_with_dict_suffix(content: str, names: set[str]) -> str:
    """Append `Dict` to every whole-word occurrence of each name in `names`.

    Order doesn't matter because `\\b` anchors in the pattern prevent partial-prefix matches.
    """
    for name in names:
        content = re.sub(rf'\b{re.escape(name)}\b', f'{name}Dict', content)
    return content


def postprocess_models(path: Path) -> bool:
    """Apply `_models.py`-specific fixes. Returns True if the file changed."""
    original = path.read_text()
    fixed = fix_discriminators(original)
    fixed = deduplicate_error_type_enum(fixed)
    fixed = add_docs_group_decorators(fixed, 'Models')
    if fixed == original:
        return False
    path.write_text(fixed)
    return True


def postprocess_typeddicts(path: Path) -> bool:
    """Apply `_typeddicts.py`-specific fixes. Returns True if the file changed."""
    original = path.read_text()
    pruned, kept = prune_typeddicts(original, RESOURCE_INPUT_TYPEDDICTS)
    renamed = rename_with_dict_suffix(pruned, kept)
    flattened = flatten_empty_typeddicts(renamed)
    final = add_docs_group_decorators(flattened, 'Typed dicts')
    if final == original:
        return False
    path.write_text(final)
    return True


def run_ruff(paths: list[Path]) -> None:
    """Run `ruff check --fix` and `ruff format` on the given files (single subprocess per phase)."""
    paths_s = [str(p) for p in paths]
    subprocess.run(['uv', 'run', 'ruff', 'check', '--fix', *paths_s], check=True, cwd=REPO_ROOT)  # noqa: S603, S607
    subprocess.run(['uv', 'run', 'ruff', 'format', *paths_s], check=True, cwd=REPO_ROOT)  # noqa: S603, S607


def main() -> None:
    changed: list[Path] = []
    if postprocess_models(MODELS_PATH):
        changed.append(MODELS_PATH)
        print(f'Fixed generated models in {MODELS_PATH}')
    else:
        print('No fixes needed for _models.py')

    if postprocess_typeddicts(TYPEDDICTS_PATH):
        changed.append(TYPEDDICTS_PATH)
        print(f'Pruned and renamed TypedDicts in {TYPEDDICTS_PATH}')
    else:
        print('No fixes needed for _typeddicts.py')

    if changed:
        run_ruff(changed)


if __name__ == '__main__':
    main()
