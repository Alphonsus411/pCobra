#!/usr/bin/env python3
from __future__ import annotations

import ast
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"


def _is_forbidden_import(node: ast.AST) -> bool:
    if isinstance(node, ast.Import):
        return any(alias.name == "scripts" or alias.name.startswith("scripts.") for alias in node.names)
    if isinstance(node, ast.ImportFrom):
        if node.module is None:
            return False
        return node.module == "scripts" or node.module.startswith("scripts.")
    return False


def main() -> int:
    violations: list[tuple[Path, int, str]] = []
    for path in sorted(SRC_ROOT.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if _is_forbidden_import(node):
                snippet = (node.module if isinstance(node, ast.ImportFrom) else ", ".join(a.name for a in node.names))
                violations.append((path, node.lineno, snippet))

    if violations:
        print("Se detectaron imports prohibidos a scripts.* dentro de src/:")
        for path, lineno, snippet in violations:
            rel = path.relative_to(SRC_ROOT.parent)
            print(f" - {rel}:{lineno}: {snippet}")
        return 1

    print("OK: no se detectaron imports a scripts.* dentro de src/.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
