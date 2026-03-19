"""Fix async client docstrings to match their sync counterparts."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import TYPE_CHECKING

from ._utils import iter_docstring_mismatches, load_package, walk_modules

if TYPE_CHECKING:
    from griffe import Module

Replacement = tuple[str, str, str, bool]
"""A pending docstring replacement: (class_name, method_name, correct_docstring, has_existing)."""

EditOp = tuple[str, int, int | None, str]
"""A source-level edit operation: (op_type, start_line, end_line, formatted_docstring)."""

MethodIndex = dict[tuple[str, str], ast.FunctionDef | ast.AsyncFunctionDef]
"""Mapping of (class_name, method_name) to the corresponding AST node."""


def _format_docstring(content: str, indent: str) -> str:
    """Format a docstring with proper indentation and triple quotes."""
    lines = content.split('\n')
    if len(lines) == 1:
        return f'{indent}"""{lines[0]}"""\n'

    result_lines = [f'{indent}"""{lines[0]}']
    for line in lines[1:]:
        if line.strip():
            result_lines.append(f'{indent}{line}')
        else:
            result_lines.append('')
    result_lines.append(f'{indent}"""')
    return '\n'.join(result_lines) + '\n'


def _build_method_index(tree: ast.AST) -> MethodIndex:
    """Build a lookup of (class_name, method_name) -> method AST node."""
    index: MethodIndex = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.body:
                    index[(node.name, item.name)] = item
    return index


def _build_edit_ops(method_index: MethodIndex, replacements: list[Replacement]) -> list[EditOp]:
    """Build a list of edit operations from the collected replacements."""
    ops: list[EditOp] = []

    for class_name, method_name, correct_docstring, has_existing in replacements:
        method = method_index.get((class_name, method_name))
        if not method:
            continue

        first_stmt = method.body[0]

        if has_existing:
            if not (
                isinstance(first_stmt, ast.Expr)
                and isinstance(first_stmt.value, ast.Constant)
                and isinstance(first_stmt.value.value, str)
                and first_stmt.end_lineno is not None
            ):
                continue
            indent = ' ' * first_stmt.col_offset
            formatted = _format_docstring(correct_docstring, indent)
            ops.append(('replace', first_stmt.lineno, first_stmt.end_lineno, formatted))
        else:
            indent = ' ' * first_stmt.col_offset
            formatted = _format_docstring(correct_docstring, indent)
            ops.append(('insert', first_stmt.lineno, None, formatted))

    return ops


def _apply_edit_ops(source_lines: list[str], ops: list[EditOp]) -> list[str]:
    """Apply edit operations to source lines (bottom-up to preserve line numbers)."""
    for op_type, start_line, end_line, formatted in sorted(ops, key=lambda x: x[1], reverse=True):
        formatted_lines = formatted.splitlines(keepends=True)
        if op_type == 'replace':
            source_lines[start_line - 1 : end_line] = formatted_lines
        elif op_type == 'insert':
            source_lines[start_line - 1 : start_line - 1] = formatted_lines

    return source_lines


def _fix_module(module: Module, replacements: list[Replacement]) -> int:
    """Fix docstrings in a single module. Returns the number of fixes applied."""
    if not replacements:
        return 0

    filepath = module.filepath
    if not isinstance(filepath, Path):
        return 0

    source = filepath.read_text(encoding='utf-8')
    tree = ast.parse(source)
    method_index = _build_method_index(tree)

    ops = _build_edit_ops(method_index, replacements)
    if not ops:
        return 0

    source_lines = source.splitlines(keepends=True)
    source_lines = _apply_edit_ops(source_lines, ops)

    updated = ''.join(source_lines)
    if updated != source:
        filepath.write_text(updated, encoding='utf-8')

    return len(ops)


def main() -> None:
    """Fix all async client methods with missing or mismatched docstrings."""
    package = load_package()

    # Group replacements by module filepath.
    module_replacements: dict[str, tuple[Module, list[Replacement]]] = {}
    for module in walk_modules(package):
        filepath = module.filepath
        if filepath:
            module_replacements[str(filepath)] = (module, [])

    for (
        async_class,
        async_method,
        _sync_class,
        _sync_method,
        expected_docstring,
        has_existing,
    ) in iter_docstring_mismatches(package):
        # Find the module this class belongs to.
        mod = async_class.parent
        if mod and str(mod.filepath) in module_replacements:
            label = 'Updating' if has_existing else 'Adding missing'
            print(f'  {label} docstring for "{async_class.name}.{async_method.name}"')
            module_replacements[str(mod.filepath)][1].append(
                (async_class.name, async_method.name, expected_docstring, has_existing)
            )

    fixed_count = sum(_fix_module(module, repls) for module, repls in module_replacements.values())

    if fixed_count:
        print(f'\nFixed {fixed_count} docstring(s).')
    else:
        print('All async docstrings are already in sync.')


if __name__ == '__main__':
    main()
