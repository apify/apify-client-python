"""Post-process datamodel-codegen output to fix known issues and prune the TypedDict file.

Applied to `_models.py`:
- Fix discriminator field names that use camelCase instead of snake_case (known issue with discriminators on schemas
  referenced from array items).
- Rewrite every `class X(StrEnum)` as `X = Literal[...]` so downstream code can pass plain strings
  (and reuse the named alias in resource-client signatures) instead of enum members.
- Move the resulting `X = Literal[...]` definitions into `_literals.py`, leaving `_models.py` importing them — so
  consumers can depend on a dedicated literals module without pulling in every Pydantic model.
- Add `@docs_group('Models')` to every model class (plus the required import).

Applied to `_typeddicts.py`:
- Keep only the TypedDicts actually used as resource-client method inputs (plus their transitive dependencies).
  The file is generated in full by datamodel-codegen; the trimming happens here.
- Rename every kept class to add a `Dict` suffix so it doesn't clash with the Pydantic model name
  (e.g. `WebhookCreate` -> `WebhookCreateDict`) and rewire references.
- Generate a camelCase sibling for every kept TypedDict (`FooDict` -> `FooCamelDict`) so users can pass API-shaped
  dicts and still satisfy the type checker. Field identifiers are looked up in the Pydantic alias map extracted
  from `_models.py`; nested TypedDict refs are rewired to the camel variant.
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
LITERALS_PATH = PACKAGE_DIR / '_literals.py'
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


def _collapse_blank_lines(content: str) -> str:
    """Collapse runs of 3+ blank lines down to exactly 3, leaving at most 2 blank lines between symbols."""
    return re.sub(r'\n{3,}', '\n\n\n', content)


def _ensure_typing_import(content: str, name: str) -> str:
    """Append `name` to the `from typing import ...` line if not already imported.

    Assumes the single-line import form datamodel-codegen emits; ruff re-wraps afterwards.
    """
    typing_import = re.search(r'from typing import[^\n]+', content)
    if typing_import is None or name in typing_import.group(0):
        return content
    return re.sub(
        r'(from typing import )([^\n]+)',
        lambda m: f'{m.group(1)}{m.group(2)}, {name}',
        content,
        count=1,
    )


def _base_names(node: ast.ClassDef) -> set[str]:
    """Return the set of unsubscripted base-class names of `node`."""
    return {b.id for b in node.bases if isinstance(b, ast.Name)}


def fix_discriminators(content: str) -> str:
    """Replace camelCase discriminator values with their snake_case equivalents."""
    for camel, snake in DISCRIMINATOR_FIXES.items():
        content = re.sub(
            rf"discriminator='{camel}'",
            f"discriminator='{snake}'",
            content,
        )
    return content


def convert_enums_to_literals(content: str) -> str:
    """Rewrite every `class X(StrEnum): ...` into an `X = Literal[...]` alias.

    Each member assignment (`NAME = 'value'`) contributes its string value to the literal in
    declaration order. The class docstring, if present, is preserved as a trailing bare-string
    docstring after the alias — matching the field-doc convention datamodel-codegen already uses
    elsewhere in the generated file.

    Runs before `add_docs_group_decorators`, so the enum classes have no `@docs_group` decorator
    to strip. The `from enum import StrEnum` import is left alone and removed by ruff's F401 fix.
    """
    tree = ast.parse(content)
    lines = content.split('\n')
    replacements: list[tuple[int, int, list[str]]] = []

    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        base_names = _base_names(node)
        if 'StrEnum' not in base_names:
            continue

        values: list[str] = [
            stmt.value.value
            for stmt in node.body
            if isinstance(stmt, ast.Assign)
            and len(stmt.targets) == 1
            and isinstance(stmt.targets[0], ast.Name)
            and isinstance(stmt.value, ast.Constant)
            and isinstance(stmt.value.value, str)
        ]
        docstring = ast.get_docstring(node)

        new_lines: list[str] = [f'{node.name} = Literal[']
        new_lines.extend(f'    {v!r},' for v in values)
        new_lines.append(']')
        if docstring is not None:
            if '\n' in docstring:
                new_lines.append('"""')
                new_lines.extend(docstring.splitlines())
                new_lines.append('"""')
            else:
                new_lines.append(f'"""{docstring}"""')

        assert node.end_lineno is not None  # noqa: S101
        replacements.append((node.lineno - 1, node.end_lineno, new_lines))

    if not replacements:
        return content

    # Replace in reverse order so earlier slice indices stay valid after each splice.
    for start, end, new in sorted(replacements, key=lambda r: r[0], reverse=True):
        lines[start:end] = new

    return _collapse_blank_lines('\n'.join(lines))


LITERALS_FILE_HEADER = """\
# generated by postprocess_generated_models

from __future__ import annotations

from typing import Literal


"""


def _is_literal_alias(node: ast.stmt) -> bool:
    """Return True if `node` is a top-level `Name = Literal[...]` statement."""
    return (
        isinstance(node, ast.Assign)
        and len(node.targets) == 1
        and isinstance(node.targets[0], ast.Name)
        and isinstance(node.value, ast.Subscript)
        and isinstance(node.value.value, ast.Name)
        and node.value.value.id == 'Literal'
    )


def split_literals_to_file(content: str) -> tuple[str, str]:
    """Move every top-level `Name = Literal[...]` block into a separate literals module.

    Walks the top-level AST, collects each literal alias plus its trailing bare-string docstring,
    deletes them from `_models.py`, and rebuilds `_literals.py` from the blocks
    in original order. The models content gains a `from apify_client._literals import ...`
    line so Pydantic can still resolve the forward references in field annotations.

    Returns `(new_models_content, literals_file_content)`. If no literal aliases are found, the
    models content is returned unchanged and the literals content is empty.
    """
    tree = ast.parse(content)
    lines = content.split('\n')

    blocks: list[tuple[int, int, str]] = [
        (node.lineno - 1, end_line, name)
        for name, node, end_line in _extract_top_level_symbols(tree)
        if _is_literal_alias(node)
    ]

    if not blocks:
        return content, ''

    literal_lines: list[str] = []
    for start, end, _ in blocks:
        literal_lines.extend(lines[start:end])
        literal_lines.append('')
        literal_lines.append('')

    new_lines = lines[:]
    for start, end, _ in sorted(blocks, key=lambda b: b[0], reverse=True):
        del new_lines[start:end]

    # Inject the import right after the last existing `from apify_client.` import so ruff/isort
    # keep the final ordering stable.
    names = sorted(name for _, _, name in blocks)
    import_line = f'from apify_client._literals import {", ".join(names)}'
    insert_at = next(
        (idx + 1 for idx in range(len(new_lines) - 1, -1, -1) if new_lines[idx].startswith('from apify_client.')),
        None,
    )
    if insert_at is None:
        raise RuntimeError('No `from apify_client.` import found in generated models to anchor literals import')
    new_lines.insert(insert_at, import_line)

    models_content = _collapse_blank_lines('\n'.join(new_lines))
    literals_content = _collapse_blank_lines(LITERALS_FILE_HEADER + '\n'.join(literal_lines))
    return models_content, literals_content


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
        base_names = _base_names(node)
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

    return _ensure_typing_import(_collapse_blank_lines('\n'.join(lines)), 'TypeAlias')


def _is_string_expr(node: ast.stmt) -> bool:
    """Return True if `node` is a bare string expression (e.g. a module-level docstring)."""
    return isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str)


def _extract_top_level_symbols(tree: ast.Module) -> list[tuple[str, ast.stmt, int]]:
    """Return (name, node, end_line) for every top-level class or type-alias statement.

    If a top-level string expression immediately follows a symbol, it is absorbed into that
    symbol's `end_line` so they get pruned together (datamodel-codegen emits the schema description
    for type-alias statements as a bare string right after the alias).
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
        elif isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id

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
    return _collapse_blank_lines('\n'.join(pruned)), kept


def rename_with_dict_suffix(content: str, names: set[str]) -> str:
    """Append `Dict` to every whole-word occurrence of each name in `names`.

    Order doesn't matter because `\\b` anchors in the pattern prevent partial-prefix matches.
    """
    for name in names:
        content = re.sub(rf'\b{re.escape(name)}\b', f'{name}Dict', content)
    return content


def _extract_alias_from_field_call(field_call: ast.Call) -> str | None:
    """Return the `alias=` kwarg value from a `Field(...)` call, or None if not present."""
    for kw in field_call.keywords:
        if kw.arg == 'alias' and isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
            return kw.value.value
    return None


def _extract_class_field_aliases(class_node: ast.ClassDef) -> dict[str, str]:
    """Return `{snake_field: api_field}` for every annotated field declared on `class_node`.

    Fields without a `Field(alias=...)` map to themselves (their declared Python name matches the API name — typical
    for single-word fields like `url`, `id`).
    """
    aliases: dict[str, str] = {}
    for stmt in class_node.body:
        if not isinstance(stmt, ast.AnnAssign) or not isinstance(stmt.target, ast.Name):
            continue
        field_name = stmt.target.id
        if field_name == 'model_config':
            continue
        # Default: no alias means snake name == API name.
        api_name = field_name
        # Walk the annotation to find a nested `Field(alias='...')` call inside `Annotated[...]`.
        for sub in ast.walk(stmt.annotation):
            if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name) and sub.func.id == 'Field':
                found = _extract_alias_from_field_call(sub)
                if found is not None:
                    api_name = found
                    break
        aliases[field_name] = api_name
    return aliases


def build_alias_map(models_source: str) -> dict[str, dict[str, str]]:
    """Return `{ModelName: {snake_field: api_field}}` for every Pydantic model in `models_source`.

    The map is the source of truth for camelCase field names: it captures both `Field(alias=...)` overrides
    and the bare-name case (single-word fields without an alias). Used when synthesizing camelCase TypedDict
    variants so the API spelling round-trips losslessly.
    """
    tree = ast.parse(models_source)
    return {node.name: _extract_class_field_aliases(node) for node in tree.body if isinstance(node, ast.ClassDef)}


def _camel_dict_name(snake_name: str) -> str:
    """Insert `Camel` before the trailing `Dict` (e.g. `RequestDict` -> `RequestCamelDict`)."""
    if not snake_name.endswith('Dict'):
        raise ValueError(f"Expected name to end with 'Dict': {snake_name!r}")
    return snake_name[: -len('Dict')] + 'CamelDict'


def _is_dict_str_any(node: ast.expr) -> bool:
    """Return True if `node` is a `dict[str, Any]` subscript (casing-agnostic open mapping)."""
    return isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name) and node.value.id == 'dict'


def _rename_fields_in_class_block(block: list[str], field_aliases: dict[str, str]) -> list[str]:
    """Rewrite each field declaration line in `block` using `field_aliases`.

    Matches lines of the form `<indent><snake_ident>:` and substitutes the identifier when an alias is present.
    Multi-line annotations and trailing default values are preserved verbatim because only the field name
    on the first line is replaced.
    """
    field_decl = re.compile(r'^(\s+)([a-z_][a-z0-9_]*)(\s*:)')
    out: list[str] = []
    for line in block:
        m = field_decl.match(line)
        if m is None:
            out.append(line)
            continue
        indent, name, colon = m.group(1), m.group(2), m.group(3)
        api_name = field_aliases.get(name)
        if api_name is None or api_name == name:
            out.append(line)
            continue
        out.append(f'{indent}{api_name}{colon}{line[m.end() :]}')
    return out


def _rename_typeddict_refs_in_block(block: list[str], rename_set: set[str]) -> list[str]:
    """Rewrite every whole-word occurrence of each name in `rename_set` to its camel form.

    Operates on the block as a single string so refs spanning multiple lines (e.g. annotations wrapped across lines)
    are caught.
    """
    if not rename_set:
        return block
    text = '\n'.join(block)
    # `\b` anchors already prevent partial-prefix matches; we just iterate the set in any stable
    # order. Sorting keeps the substitution deterministic across Python hash seeds.
    for snake in sorted(rename_set):
        text = re.sub(rf'\b{re.escape(snake)}\b', _camel_dict_name(snake), text)
    return text.split('\n')


def add_camel_case_typeddicts(content: str, alias_map: dict[str, dict[str, str]]) -> str:
    """Insert a camelCase sibling for every TypedDict and TypeAlias in `content`.

    For each class `<Name>Dict(TypedDict)` and each `<Name>Dict: TypeAlias = ...`, emit a sibling `<Name>CamelDict`
    directly after the original. Field identifiers are renamed using `alias_map[<Name>]`; nested TypedDict references
    in annotations are rewired to their camel variant via whole-word substitution.

    `TaskInputDict: TypeAlias = dict[str, Any]` and similar casing-agnostic aliases get a trivial camel alias too,
    so refs from other camel TypedDicts (e.g. `RequestBaseCamelDict.user_data: NotRequired[RequestUserDataCamelDict]`)
    resolve cleanly.

    Idempotent: blocks whose name already ends with `CamelDict` are skipped.
    """
    tree = ast.parse(content)
    lines = content.split('\n')

    # Pass 1: gather every snake-side symbol that needs a camel sibling.
    snake_classes: list[tuple[ast.ClassDef, int, int]] = []  # node, block_start, block_end (exclusive)
    snake_aliases: list[tuple[int, int]] = []  # block_start, block_end
    flat_aliases: list[tuple[int, str]] = []  # block_end, alias_name

    body_with_trailing_docstrings = _extract_top_level_symbols(tree)
    end_by_name: dict[str, int] = {name: end for name, _, end in body_with_trailing_docstrings}
    existing_symbols: set[str] = {name for name, _, _ in body_with_trailing_docstrings}

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            # Every class kept in `_typeddicts.py` is a TypedDict — either directly (base is `TypedDict`) or by
            # inheriting from a sibling TypedDict (e.g. `RequestDict(RequestBaseDict)`). The `Dict` suffix
            # is the load-bearing filter; the base check is informational only.
            if not node.name.endswith('Dict') or node.name.endswith('CamelDict'):
                continue
            if _camel_dict_name(node.name) in existing_symbols:
                continue
            start = node.lineno - 1
            if start > 0 and lines[start - 1].lstrip().startswith('@'):
                start -= 1
            end = end_by_name.get(node.name, node.end_lineno or node.lineno)
            snake_classes.append((node, start, end))
        elif (
            isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and isinstance(node.annotation, ast.Name)
            and node.annotation.id == 'TypeAlias'
        ):
            name = node.target.id
            if not name.endswith('Dict') or name.endswith('CamelDict'):
                continue
            if _camel_dict_name(name) in existing_symbols:
                continue
            if node.value is None:
                continue
            start = node.lineno - 1
            end = end_by_name.get(name, node.end_lineno or node.lineno)
            if _is_dict_str_any(node.value):
                flat_aliases.append((end, name))
            else:
                snake_aliases.append((start, end))

    # The rename set covers EVERY snake-side `*Dict` symbol in the file (not just the ones we need to clone)
    # so nested refs inside a cloned block still rewire correctly even on re-runs where most camel siblings
    # already exist.
    rename_set: set[str] = {
        name for name in existing_symbols if name.endswith('Dict') and not name.endswith('CamelDict')
    }

    # Pass 2: build camel blocks.
    insertions: list[tuple[int, list[str]]] = []

    for class_node, start, end in snake_classes:
        block = lines[start:end]
        renamed_refs = _rename_typeddict_refs_in_block(block, rename_set)
        field_aliases = alias_map.get(class_node.name[: -len('Dict')], {})
        camel_block = _rename_fields_in_class_block(renamed_refs, field_aliases)
        insertions.append((end, ['', *camel_block]))

    for start, end in snake_aliases:
        block = lines[start:end]
        camel_block = _rename_typeddict_refs_in_block(block, rename_set)
        insertions.append((end, ['', *camel_block]))

    for end, name in flat_aliases:
        insertions.append((end, ['', f'{_camel_dict_name(name)}: TypeAlias = dict[str, Any]']))

    # Insert in reverse line order so earlier indices stay valid.
    new_lines = lines[:]
    for after, block in sorted(insertions, key=lambda i: i[0], reverse=True):
        new_lines[after:after] = block

    return _collapse_blank_lines('\n'.join(new_lines))


def postprocess_models(models_path: Path, literals_path: Path) -> list[Path]:
    """Apply `_models.py`-specific fixes and emit `_literals.py`.

    Returns the list of paths that were (re)written.
    """
    original = models_path.read_text()
    fixed = fix_discriminators(original)
    fixed = convert_enums_to_literals(fixed)
    fixed = add_docs_group_decorators(fixed, 'Models')
    models_content, literals_content = split_literals_to_file(fixed)

    changed: list[Path] = []
    if models_content != original:
        models_path.write_text(models_content)
        changed.append(models_path)
    if literals_content:
        previous = literals_path.read_text() if literals_path.exists() else ''
        if literals_content != previous:
            literals_path.write_text(literals_content)
            changed.append(literals_path)
    return changed


def postprocess_typeddicts(path: Path, alias_map: dict[str, dict[str, str]]) -> bool:
    """Apply `_typeddicts.py`-specific fixes. Returns True if the file changed."""
    original = path.read_text()
    pruned, kept = prune_typeddicts(original, RESOURCE_INPUT_TYPEDDICTS)
    renamed = rename_with_dict_suffix(pruned, kept)
    flattened = flatten_empty_typeddicts(renamed)
    camelized = add_camel_case_typeddicts(flattened, alias_map)
    final = add_docs_group_decorators(camelized, 'Typed dicts')
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
    changed = postprocess_models(MODELS_PATH, LITERALS_PATH)
    if changed:
        for path in changed:
            print(f'Wrote {path}')
    else:
        print('No fixes needed for _models.py / _literals.py')

    alias_map = build_alias_map(MODELS_PATH.read_text())
    if postprocess_typeddicts(TYPEDDICTS_PATH, alias_map):
        changed.append(TYPEDDICTS_PATH)
        print(f'Pruned, renamed, and camelized TypedDicts in {TYPEDDICTS_PATH}')
    else:
        print('No fixes needed for _typeddicts.py')

    if changed:
        run_ruff(changed)


if __name__ == '__main__':
    main()
