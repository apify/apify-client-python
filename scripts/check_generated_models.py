"""Check that the generated models match what the committed OpenAPI snapshot produces.

Regenerating is the only way to know, so this runs codegen and then puts the working tree back exactly as it
was - a check must not rewrite tracked source files, and it must not care whether they happen to be committed.
That keeps `poe check-code` safe to run mid-change, and keeps this independent of git state.

A failure means the generated files no longer follow from `spec/openapi.json` plus the pinned tooling: either
someone edited them by hand, or a codegen/formatter upgrade changed the output. Both are fixed the same way -
run `poe generate-models` and commit the result.
"""

from __future__ import annotations

import difflib
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

GENERATED_FILES = (
    Path('src/apify_client/_models.py'),
    Path('src/apify_client/_typeddicts.py'),
    Path('src/apify_client/_literals.py'),
)


def main() -> None:
    committed = {path: (REPO_ROOT / path).read_text(encoding='utf-8') for path in GENERATED_FILES}
    drifted: list[Path] = []

    try:
        subprocess.run(['uv', 'run', 'poe', 'generate-models'], check=True, cwd=REPO_ROOT)  # noqa: S607

        for path in GENERATED_FILES:
            regenerated = (REPO_ROOT / path).read_text(encoding='utf-8')
            if regenerated == committed[path]:
                continue

            drifted.append(path)
            sys.stdout.writelines(
                difflib.unified_diff(
                    committed[path].splitlines(keepends=True),
                    regenerated.splitlines(keepends=True),
                    fromfile=f'{path} (on disk)',
                    tofile=f'{path} (regenerated)',
                )
            )
    finally:
        for path, content in committed.items():
            (REPO_ROOT / path).write_text(content, encoding='utf-8', newline='\n')

    if drifted:
        print(
            f'\n{len(drifted)} generated file(s) do not match `spec/openapi.json`: '
            f'{", ".join(str(path) for path in drifted)}.\n'
            'Run `uv run poe generate-models` and commit the result.',
            file=sys.stderr,
        )
        sys.exit(1)

    print('Generated models match the committed OpenAPI specification snapshot.')


if __name__ == '__main__':
    main()
